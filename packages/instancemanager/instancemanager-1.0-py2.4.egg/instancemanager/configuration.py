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
import tempfile
import types
import urllib
import utils
from config import DEBUGCONFIGCHANGES

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
            self.reloadConfig(project)

    def reloadConfig(self, project):
        self._loadConfigData(project)
        self._processReplacements()
        self._zopeConfigReplacements()
        self._zeoConfigReplacements()

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
            else:
                log.debug("Copying of skeleton file '%s' not needed.",
                          target)
        log.debug("Done with the skeleton files.")

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
        else:
            log.debug("No project config file. We could be "
                      "bootstrapping.")
        if self.configData['is_windows']:
            # finally, adjust the config for windows if need be
            #log.debug("configData is now %r.", self.configData)
            pass
            
    def _processReplacements(self):
        """ Processes the replacement strings in the configData recursively
        
        >>> config = {
        ... 'zope_instance_template': '%(user_dir)s/instances/%(project)s', 
        ... 'zope_location_template': '~/zope/%(zope_version)s', 
        ... 'user_dir': '~', 
        ... 'project': 'myproject', 
        ... 'zope_version': 'Zope-2.9.5'}

        Make a configuration to test
        >>> c=Configuration()
        
        Give it the fake configData defined above
        >>> c.__setattr__('configData', config)
        
        Process that configData to do all substitutions
        >>> c._processReplacements()
        
        Test the results
        >>> cks=c.configData.keys()
        >>> cks.sort()  
        
        Standardise the test result by replacing platform dependent strings
        >>> u=os.path.expanduser('~')   
        >>> f='%s:%s -> %s'    
        
        Print and compare  
        >>> for k in cks:
        ...     print f % (k, config[k], c.configData[k].replace(u, 'HOME') )
        project:myproject -> myproject
        user_dir:~ -> HOME
        zope_instance_template:%(user_dir)s/instances/%(project)s -> HOME/instances/myproject
        zope_location_template:~/zope/%(zope_version)s -> HOME/zope/Zope-2.9.5
        zope_version:Zope-2.9.5 -> Zope-2.9.5
        """ 
        result={}    
        config=self.configData
        while True: 
            for k in config.keys():
                val=config[k]
                if type(val) == types.StringType:
                    try:
                        result[k] = os.path.expanduser(val % config)
                    except KeyError:
                        #clientname is not defined at start
                        #do most of it, and come back later.
                        result[k] = os.path.expanduser(val) 
                else:
                    result[k] = val   # non-strings pass through unchanged
            if config == result: break
            config=result  # go around again
        self.configData=result
        
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
        log.debug("configData is now...")
        configItems=self.configData.items()
        configItems.sort()
        for item in configItems:
            log.debug(" %s: %r." % item )

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

    def _zopeConfigReplacements(self):
        """Add items to be replaced in the zope config.
        """

        self.configData['zopeConfigChanges'] = {}
        changes = self.configData['zopeConfigChanges']
        if self.configData['development_machine']:
            # Add the standard debug_mode, verbose_security stuff.
            changes.update(DEBUGCONFIGCHANGES)
        listenIpAddress = self.configData['listen_ip_address']
        if listenIpAddress:
            new = 'ip-address %s ' % listenIpAddress
            changes['ip-address 127.0.0.1'] = new
            log.debug("Added desired ip-address change to list of "
                      "config changes.")

    def _zeoConfigReplacements(self):
        """Add items to be replaced in the zeo config.
        """

        self.configData['zeoConfigChanges'] = {}
        changes = self.configData['zeoConfigChanges']
        monitorAddress = self.configData['monitor_port']
        if monitorAddress:
            new = 'monitor-address %s' % str(monitorAddress)
            changes['monitor-address'] = new
            
    def zopeDir(self):
        """Return location of zope directory.
        """

        return self.configData['zope_location_template']

    def zeoDir(self):
        """Return location of the zope zeo directory.
        """

        return self.configData['zeo_server_template']

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

        return self.configData['zope_instance_template']

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

        return self.configData['datafs_template']

    def zopeconf(self):
        """Return location of the pre-made zope.conf.
        """

        return self.configData['zopeconf_template']

    def zeoconf(self):
        """Return location of the pre-made zeo.conf.
        """

        return self.configData['zeoconf_template']

    def symlinkBaseDir(self):
        """Return location of the symlink base directory.
        """

        return self.configData['symlink_basedir_template']

    def symlinkbundleBaseDir(self):
        """Return location of the symlinkbundle base directory.
        """

        return self.configData['symlinkbundle_basedir_template']

    def configBaseDir(self):
        """Return location of the symlink base directory.
        """

        return self.configData['config_basedir_template']

    def archiveBaseDir(self):
        """Return location of the tgz base directory.
        """

        return self.configData['archive_basedir_template']

    def archivebundleBaseDir(self):
        """Return location of the tgz bundle base directory.
        """

        return self.configData['archivebundle_basedir_template']

    def backupBaseDir(self):
        """Return location where backups will be saved.

        By default, this basedir includes the product name, for
        instance as ~/backups/vanrees/.
        """

        return self.configData['backup_basedir_template']

    def numberOfBackups(self):
        """Return the number of full backups to keep
        """
        no = self.configData['number_of_backups']
        return int(no)

    def snapshotBaseDir(self):
        """Return location where snapshot backups will be saved.
        """

        return self.configData['snapshot_basedir_template']

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
        """Return both config and product sources.
        """
        return self.config_sources(instanceDir) + self.product_sources(instanceDir)


    def product_sources(self, instanceDir):
        """Return all product sources as ...Source instances.

        No config sources.  see config_sources() below
        """

        sourceListNames = [s for s in self.configData.keys()
                           if s.endswith('_sources')
                           and not s.startswith('config')]
        # Sort the sources so the order of installation is clear.
        bundles = [s for s in sourceListNames if s.find('bundle') != -1]
        singles = [s for s in sourceListNames if s.find('bundle') == -1]
        sourceListNames = bundles + singles

        return self._createWrappedSourcesList(instanceDir, sourceListNames)

    def config_sources(self, instanceDir):
        """Return all config sources as ConfigSource instances.
        """

        sourceListNames = [s for s in self.configData.keys()
                           if s.endswith('_sources')
                           and s.startswith('config')]

        return self._createWrappedSourcesList(instanceDir, sourceListNames)

    def _createWrappedSourcesList(self, instanceDir, names):
        """Return a list of sources mentioned in 'names', wrapped as
           ...Source instances.
        """
        _sources = []

        for sourceListName in names:
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


class BootstrapConfiguration(Configuration):
    """Takes care of reading the configuration files.

    The configuration is handled in a layered manner, with the
    possibility to overwrite the defaults of the previous
    layer. Providing sensible defaults is a key issue here.
    """

    def __init__(self, project=None, bootstrap=None):
        """Load all configuration pertaining to the project.
        """

        Configuration.__init__(self, project)
        bootstrapFilename = self._grabBootstrapFilename(bootstrap)
        self._loadBootstrapData(bootstrapFilename)
        self._processReplacements()

    def _grabBootstrapFilename(self, bootstrap):
        log.debug("Grabbing filename for '%s'.", bootstrap)
        if bootstrap.startswith('http'):
            log.debug("Remote file, downloading it.")
            target = tempfile.mktemp()
            urllib.urlretrieve(bootstrap, target)
            return target
        else:
            log.debug("No remote file, returning absolute path.")
            return os.path.abspath(bootstrap)

    def _loadBootstrapData(self, filename):
        bootstrapData = self._loadUserConfigModule(
            'bootstrap',
            absolutePath=filename)
        if bootstrapData:
            self._collectAttributes(bootstrapData)
        else:
            log.critical("Could not find %s file.", filename)
            sys.exit(1)

    def configBaseDir(self):
        """Return location of the symlink base directory.
        """

        return self.configData['config_basedir_template']

    def configSource(self, instanceDir):
        """ Return only the config source for bootstrapping
        """
        imsource = sources.ConfigSource(sourceConfig=self.configData['config_sources'][0],
                              config=self, instanceDir=instanceDir)
        return imsource

    def customizationParameters(self):
        """Return the parameters we suggest the user to modify.
        """

        return []

    def symlinkableConfiguration(self):
        """Return the path of the IM config that needs symlinking.

        """

        config = self.configData.get('bootstrap_config', None)
        if not config:
            return None
        return os.path.join(self.configBaseDir(),
                            config)

    def contentForLocal(self):
        default = """## Adapt to local needs if needed. Port, user and password
## currently use the default from your project file.
# port = '8080'
# user = 'test'
# password = 'test'
"""        
        return self.configData.get('bootstrap_local_content', default)
