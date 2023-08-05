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

        * Site-wide defaults (/etc/instancemanager/sitedefaults.py).

        * User defaults (userdefaults.py in the config dir).

        * Per-project extra configuration (projectname.py in the
          config dir).

       The variables imported from these files should be placed in
        self.configData.

        For the user defaults and the project configuration, you can
        add a file named like the defaults/project config, but
        prefixed with 'local-'. That's handy for usernames and
        passwords that you don't want in subversion, for instance.

        """

        log.debug("Loading our configuration defaults.")
        # First set user_dir and project (needed for templates)
        userDir = os.path.expanduser('~')
        self.configData['user_dir'] = userDir
        self.configData['project'] = project
        # set is_windows if running on windows platform
        if os.name == "nt":
            self.configData['is_windows'] = True
            log.debug("Instance is running on Windows OS")
        else:
            self.configData['is_windows'] = False

        import defaults
        self._collectAttributes(defaults)
        # Second: site-wide defaults.
        siteDefaults = self._loadUserConfigModule('SiteDefaults',
            absolutePath=config.SITECONFIG)
        if siteDefaults:
            self._collectAttributes(siteDefaults)
        else:
            log.debug("No site-wide defaults file.")
        # Third, user defaults (including secret).
        userDefaults = self._loadUserConfigModule('userdefaults')
        if userDefaults:
            self._collectAttributes(userDefaults)
        else:
            log.critical("User defaults could not be read from your "
                         "config directory.")
            sys.exit(1)
        secretUserDefaults = self._loadUserConfigModule(
            config.SECRET_PREFIX+'userdefaults')
        if secretUserDefaults:
            self._collectAttributes(secretUserDefaults)
        else:
            log.debug("No secret user defaults file.")
        if project:
            # Fourth: project defaults (including secret).
            projectDefaults = self._loadUserConfigModule(project)
            if projectDefaults:
                self._collectAttributes(projectDefaults)
            else:
                log.warn("Project config file for %s not found "
                         "in your config directory.", project)
            secretProjectDefaults = self._loadUserConfigModule(
                config.SECRET_PREFIX+project)
            if secretProjectDefaults:
                self._collectAttributes(secretProjectDefaults)
            else:
                log.debug("No secret project config file.")
        if self.configData['is_windows']:
            # finally, adjust the config for windows if need be
            #log.debug("configData is now %r.", self.configData)
            pass

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

    def _loadUserConfigModule(self, name, absolutePath=None):
        """Return module loaded from the user's config dir.

        If an absolute path is specified, use that as the filename.
        """

        if absolutePath:
            moduleFile = absolutePath
            log.debug("Trying to load config file at '%s'.",
                      moduleFile)
        else:
            log.debug("Trying to load user config module '%s'.", name)
            moduleFile = os.path.join(self.configDir, name+'.py')
        # Check if the file exists
        if not os.path.exists(moduleFile):
            log.debug("Couldn't find '%s'.", moduleFile)
            return None
        # Import it.
        module = imp.load_source(name, moduleFile)
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
        zopePort = self.instancePort()
        result = zopePort + offset
        return unicode(result)

    def instanceDir(self):
        """Return location of the zope instance directory.
        When using zeo: this is the location of the first zeo client.
        """

        return self.expandTemplate('zope_instance_template')

    def instancePort(self):
        """Return calculated port number as a string.
        When using zeo: this is the port of the first zeo client.
        """
        return int(self.configData['port'])

    def zeoClientDirs(self):
        """Return locations of zeo client directories.
        This is a list of e.g. path/test, path/test1, path/test2.
        """
        return [instance['dir'] for instance in self.zeoClients()]

    def zeoClientPorts(self):
        """Return ports of zeo clients.
        """
        return [instance['port'] for instance in self.zeoClients()]

    def zeoClientPort(self, dir):
        """Return port of zeo clients in directory dir.
        """
        ports = [client['port'] for client in self.zeoClients()
                 if client['dir'] == dir]
        # The following Exceptions are very unlikely, but let's test
        # them anyway.
        if len(ports) == 0:
            raise Exception, 'Internal instancemanager error: no port found for zeo client %s' % dir
        elif len(ports) > 1:
            raise Exception, 'Internal instancemanager error: more than one port found for zeo client %s' % dir
        else:
            return ports[0]

    def zeoClients(self):
        """Return locations and ports of zeo client directories.
        
        This is a list of tuples where the items are e.g. path/test,
        path/test1, path/test2 and the values are the corresponding
        port numbers.
        """
        useZeo = self.configData['use_zeo']
        if useZeo:
            number = int(self.configData['number_of_zeo_clients'])
            if number <= 0:
                raise Exception, 'number_of_zeo_clients should be 1 or more.'
        else:
            number = 1
        zeos = []
        offset = int(self.configData['zeoport_offset'])
        simple = self.instanceDir()
        port = self.instancePort()
        reserved = int(self.zeoPort())
        zeos.append({'dir': simple, 'port': port})
        for i in range(1, number):
            port = port + offset
            if port == reserved:
                port = port + offset
            zeos.append({'dir': simple + str(i), 'port': port})
        return zeos
        
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

    def numberOfBackups(self):
        """Return the number of full backups to keep
        """
        no = self.configData['number_of_backups']
        return int(no)

    def snapshotBaseDir(self):
        """Return location where snapshot backups will be saved.
        """

        return self.expandTemplate('snapshot_basedir_template')

    def databaseBaseDir(self):
        """Return the location of the instance database file.

        Keep track of eventual zeo usage.
        """

        useZeo = self.configData['use_zeo']
        if useZeo:
            baseDir = self.zeoDir()
        else:
            baseDir = self.instanceDir()
        return os.path.join(baseDir, 'var')

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

    def sources(self, instanceDir):
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
                wrappedSource = klass(sourceConfig=source, config=self,
                                      instanceDir=instanceDir)
                _sources.append(wrappedSource)
        return _sources
        
    def mkZopeInstanceCommand(self):
        command = 'mkzopeinstance.py'
        if utils.isZope3(self):
            command = 'mkzopeinstance'
        return command

    def mkZeoInstanceCommand(self):
        command = 'mkzeoinstance.py'
        if utils.isZope3(self):
            command = 'mkzeoinstance'
        return command
        
    def instanceParams(self):
        params = '-u %s:%s -d %s' % (self.configData['user'],
                                     self.configData['password'],
                                     self.instanceDir(),)
        if utils.isZope3(self):
            params = params + ' -m %s' % self.configData['z3_pw_manager']
        return params