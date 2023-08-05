"""Provides Configuration class that reads the configuration files.
"""

import config
import imp # imp exposes the python import mechanism.
import logging
import os
import os.path
import shutil
import sources
import sys
import utils

log = logging.getLogger('configuration')

renamedAttrs = {'tgz_sources': 'archive_sources',
   'tgz_basedir_template': 'archive_basedir_template',
   'tgzbundle_sources': 'archivebundle_sources',
   'tgzbundle_basedir_template': 'archivebundle_basedir_template'}

class Configuration(object):
    """Takes care of reading the configuration files.

    The configuration is handled in a layered manner, with the
    possibility to overwrite the defaults of the previous
    layer. Providing sensible defaults is a key issue here.
    """

    def __init__(self, project=None):
        """Load all configuration pertaining to the project.
        """

        self._checkConfigDir()
        self.configData = {}
        if project:
            self._loadConfigData(project)

    def _checkConfigDir(self):
        """Check (and possibly fix) the config directory.
        """

        log.debug("Checking configuration directory...")
        userDir = os.path.expanduser('~')
        self.configDir = os.path.join(userDir,
                                      config.CONFIGDIR)
        log.debug("Config directory is '%s'.", self.configDir)
        utils.makeDir(self.configDir)

        log.debug("Copying skeleton files if needed...")
        ourDir = os.path.dirname(os.path.abspath(__file__))
        skeletonDir = os.path.join(ourDir, 'skeleton')
        log.debug("Skeleton dir: '%s'.", skeletonDir)
        skeletonFiles = [f for f in os.listdir(skeletonDir)
                         if (f.endswith('.txt')
                         or f.endswith('.py'))]
        log.debug("Found the following skeleton files: %r.",
                  skeletonFiles)
        for skeletonFile in skeletonFiles:
            source = os.path.join(skeletonDir, skeletonFile)
            target = os.path.join(self.configDir, skeletonFile)
            if not os.path.exists(target):
                shutil.copy(source, target)
                log.info("Copied skeleton file to '%s'.", target)
                
    def _loadConfigData(self, project=None):
        """Recursively load configuration data.

        Sources in increasing order of preference:

        * Our own defaults (defaults.py).

        * User defaults (userdefaults.py in the config dir).

        * Per-project extra configuration (projectname.py in the
          config dir).

       The variables imported from these files should be placed in
        self.configData.  
        """

        log.debug("Loading our configuration defaults.")
        # First set user_dir and project (needed for templates)
        userDir = os.path.expanduser('~')
        self.configData['user_dir'] = userDir
        self.configData['project'] = project
        import defaults
        self._collectAttributes(defaults)
        userDefaults = self._loadUserConfigModule('userdefaults')
        self._collectAttributes(userDefaults)
        secretUserDefaults = self._loadUserConfigModule(config.SECRET_PREFIX+'userdefaults')
        if secretUserDefaults:
            self._collectAttributes(secretUserDefaults)
        if project:
            projectDefaults = self._loadUserConfigModule(project)
            self._collectAttributes(projectDefaults)
            secretSettings = self._loadUserConfigModule(config.SECRET_PREFIX+project)
            if secretSettings:
                self._collectAttributes(secretSettings)
            
    def _fixupRenamedAttributes(self,attribute):
        return renamedAttrs.get(attribute, attribute)

    def _collectAttributes(self, module):
        """Collect module's attributes into self.configData.
        """

        attributes = dir(module)
        attributes = [a for a in attributes
                      if not a.startswith('_')]
        log.debug("Found attributes %r.", attributes)
        tempDict = {}
        for attribute in attributes:
            dattribute = self._fixupRenamedAttributes(attribute)
            tempDict[dattribute] = getattr(module, attribute)
        self.configData.update(tempDict)
        log.debug("configData is now %r.", self.configData)
    oneshotMsgs={'defaults': (
                    "You may wish to put local information common to\n"
                    " all projects, such as user and password, or local\n"
                    " directories into a file named %s.py"),
                 'project':(
                    "You may wish to put local information for this\n"
                    " project, such as user and password, into a file\n"
                    " named %s.py")
                }
    def _loadUserConfigModule(self, name):
        """Return module loaded from the user's config dir.
        """
        
        log.debug("Trying to load user config module '%s'.", name)
        moduleFile = os.path.join(self.configDir, name+'.py')
        try:
            module = imp.load_source(name, moduleFile)
        except IOError:
            if name==config.SECRET_PREFIX+'userdefaults':
                msg=self.oneshotMsgs['defaults']
                if msg: 
                    msg=msg % name
                    self.oneshotMsgs['defaults'] = None
                    log.info(msg)
            elif name.startswith(config.SECRET_PREFIX):
                msg=self.oneshotMsgs['project']
                if msg: 
                    msg=msg % name
                    self.oneshotMsgs['project'] = None
                    log.info(msg)
            else:
                msg="Couldn't find '%s' in user config dir.", name
                log.warn(msg)
            return None
        return module

    def expandTemplate(self, templateName):
        """Return filled-in template.
        """

        log.debug("Looking up template '%s'.", templateName)
        template = self.configData[templateName]
        try:
            result = template % self.configData
        except:
            # the try would fail if template is a list.
            result = template
        log.debug("Expanded template result: '%s'.", result)
        return result

    def zopeDir(self):
        """Return location of zope directory.
        """

        return self.expandTemplate('zope_location_template')

    def zeoDir(self):
        """Return location of the zope zeo directory.
        """

        return self.expandTemplate('zeo_server_template')

    def zeoPort(self):
        """Return calculated port number as a string.
        """

        offset = int(self.configData['zeoport_offset'])
        zopePort = int(self.configData['port'])
        result = zopePort + offset
        return unicode(result)

    def instanceDir(self):
        """Return location of the zope instance directory.
        """

        return self.expandTemplate('zope_instance_template')

    def datafs(self):
        """Return location of the pre-made Data.fs.
        """

        return self.expandTemplate('datafs_template')

    def zopeconf(self):
        """Return location of the pre-made zope.conf.
        """

        return self.expandTemplate('zopeconf_template')

    def zeoconf(self):
        """Return location of the pre-made zeo.conf.
        """

        return self.expandTemplate('zeoconf_template')

    def symlinkBaseDir(self):
        """Return location of the symlink base directory.
        """

        return self.expandTemplate('symlink_basedir_template')

    def symlinkbundleBaseDir(self):
        """Return location of the symlinkbundle base directory.
        """

        return self.expandTemplate('symlinkbundle_basedir_template')

    def archiveBaseDir(self):
        """Return location of the tgz base directory.
        """

        return self.expandTemplate('archive_basedir_template')

    def archivebundleBaseDir(self):
        """Return location of the tgz bundle base directory.
        """

        return self.expandTemplate('archivebundle_basedir_template')

    def backupBaseDir(self):
        """Return location where backups will be saved.

        By default, this basedir includes the product name, for
        instance as ~/backups/vanrees/. 
        """

        return self.expandTemplate('backup_basedir_template')

    def snapshotBaseDir(self):
        """Return location where snapshot backups will be saved.
        """

        return self.expandTemplate('snapshot_basedir_template')

    def databaseBaseDir(self):
        """Return the location of the instance database file.
        """

        return os.path.join(self.instanceDir(), 'var')

    def databasePath(self):
        """Return the location of the instance database file.
        
        Keep track of eventual zeo usage.
        """

        useZeo = self.configData['use_zeo']
        if useZeo:
            baseDir = self.zeoDir()
        else:
            baseDir = self.instanceDir()
        return os.path.join(baseDir, 'var', 'Data.fs')

    def zeoDatabasePath(self):
        """Return the location of the zeo database file.
        """

        return os.path.join(self.zeoDir(), 'var', 'Data.fs')

    def sources(self):
        """Return all sources as ...Source instances.
        """

        sourceListNames = [s for s in self.configData.keys()
                           if s.endswith('_sources')]
        _sources = []

        # Sort the sources so the order of installation is clear.
        bundles = [s for s in sourceListNames if s.find('bundle') != -1]
        singles = [s for s in sourceListNames if s.find('bundle') == -1]
        sourceListNames = bundles + singles

        for sourceListName in sourceListNames:
            sourceList = self.configData[sourceListName]
            klassNameBase = sourceListName.replace('_sources', '')
            klassName = klassNameBase.capitalize() + 'Source'
            klass = getattr(sources, klassName)
            log.debug("Looking for %s candidates: %r.", klassName,
                      sourceList) 
            for source in sourceList:
                wrappedSource = klass(sourceConfig=source, config=self)
                _sources.append(wrappedSource)
        return _sources
