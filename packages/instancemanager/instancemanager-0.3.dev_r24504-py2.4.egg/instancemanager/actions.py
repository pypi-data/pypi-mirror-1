"""Actions that can be performed on instances and products.

 Everything that is handy to have as a single unit of action is turned
 into an Action. They can be quite small (just stopping zope), but
 that's OK. Being able to say 'instancemanager myproject stop' from
 anywhere without having to go to the instance directory to say
 'bin/zopectl stop' saves on the number of terminals you have to keep
 open.

 The 'ACTIONS' dictionary at the end of this file is the list of
 user-visible actions. There's no need for every action to be listed
 there, so you can define Actions just for internal use, if you want.
"""

import config
import sys
import os
import os.path
import logging
import shutil
log = logging.getLogger('actions')


class Action:
    """Base class for all actions.
    """

    name = 'abstract base action'

    def __init__(self, configuration):
        self.conf = configuration

    def run(self):
        pass


class CreateInstanceAction(Action):
    """Create a zope instance.

    This will create a zope instance for you using the familiar
    'mkzopeinstance' command. The instance will be the location you
    specified in your config file. By default it will be
    '~/instances/projectname/'.

    Also, the zope.conf will be adapted in some places, like enabling
    debug mode and verbose security (for zope 2.8 and up). The port,
    username and password will be set according to the config file.
    """

    name = "Create a zope instance for your project."

    def run(self):
        python = self.conf.configData['python']
        instanceDir = self.conf.instanceDir()
        if os.path.exists(instanceDir):
            if os.getcwd() == instanceDir:
                # TODO: Also check for current working dir being
                # *below* the instance dir.
                log.error("Current working directory equals instanceDir, "
                          "which would cause an error while making "
                          "a Zope instance.")
                sys.exit(1)
            shutil.rmtree(instanceDir)
            log.debug("Removed instance dir '%s'.", instanceDir)
        mkInstance = os.path.join(self.conf.zopeDir(),
                                  'bin',
                                  'mkzopeinstance.py')
        params = '-u %s:%s -d %s' % (
            self.conf.configData['user'],
            self.conf.configData['password'],
            instanceDir,
            )
        command = ' '.join([python, mkInstance, params])
        os.system(command)
        log.info("Created zope instance in '%s'.",
                 self.conf.instanceDir())
        # TODO: port handling, security mode, debug mode
        zopeConfigFile = os.path.join(instanceDir, 'etc', 'zope.conf')
        premadeZopeconf = self.conf.zopeconf()
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
                    newLine = template % self.conf.configData
                    log.debug("Replaced %r", line)
                    log.debug("....with %r", newLine)
                    textsToChange.remove(text)
            newFile.write(newLine)
        newFile.close()
        log.info("Changed the zope config.")
                    

class CopyDatafsAction(Action):
    """Copy over a fresh, prepared, Data.fs.

    When you are developing, you might have an existing Data.fs file
    you want to use. For instance the current product database of your
    customer project that you copied for debugging purposes.

    Instancemanager looks for a database in, by default,
    '~/instances/datafs/yourproject.fs'. You can change this in your
    config. The datafs action just copies this file to the instance's
    'var/' directory.
    """

    name = "Copy over a fresh, prepared, 'Data.fs'."

    def run(self):
        source = self.conf.datafs()
        target = self.conf.databasePath()
        if not os.path.exists(source):
            log.info("No prepared Data.fs found at %s, "
                     "skipping this step.", source)
            return
        else:
            shutil.copy(source, target)
            log.info("Copied over fresh Data.fs from %s.", source)
            log.debug("Copied it to %s.", target)


class AddProductsAction(Action):
    """Rebuild the Products/ directory from scratch.

    **Warning**, this *does* remove everything in 'Products/' before
    copying over new versions. That is the whole purpose. :-) If it
    isn't your purpose, you shouldn't really be using this program.

    You can configure a variety of sources in your
    configuration. Every source is an instruction for the "products"
    action. Possible sources are svn links and .tgz files, both for
    single products or for bundles.
    """

    name = "Rebuild the Products/ directory ."

    def run(self):
        target = os.path.join(self.conf.instanceDir(), 'Products')
        shutil.rmtree(target)
        log.debug("Removed the entire %s directory.", target)
        os.mkdir(target)
        log.debug("Created it again.")
        log.debug("Adding Products...")
        for source in self.conf.sources():
            try:
                source.addProduct()
            except IOError:
                log.warn('Please fix this.')
                # XXX Maybe we want to quit with an error here.
        log.info("Rebuild the Products/ directory from scratch.")


class FreshInstallAction(Action):
    """Wipe everything and create an instance including products.

    The "fresh" action is the most brute-force way to get a fresh
    instance. It will stop zope (when running), remove the instance
    completely, set up a new instance, copy the Data.fs (if you have
    one prepared), fill your Products directory, quickreinstall your
    products and start zope. Pfew!

    This is, really, the **main action you should be using**, apart
    from the "soft" action. It makes it easy to get to a known, clear,
    fresh starting position without old cruft, locally modified files,
    etc.
    """

    name = "Wipe everything and create an instance " +\
        "including products."

    def run(self):
        subActions = [StopZopeAction,
                      CreateInstanceAction,
                      CopyDatafsAction,
                      AddProductsAction,
                      QuickreinstallAction,
                      StartZopeAction,
                      ]
        for actionClass in subActions:
            action = actionClass(self.conf)
            action.run()

        
class SoftInstallAction(Action):
    """Restart zope and call the quickreinstall script.

    The "soft" action is the **second main action** you should be
    using. It stops zope, quickreinstalls your products and starts
    zope again.

    In many development scenarios, zope will figure out you changed
    something (like a page template) when running in debug mode. To
    actually see the changes you made in python classes, you need to
    restart zope ('instancemanager yourproject restart'). When working
    on the install methods, for instance for modifying portal
    settings, the only alternative is to restart and to click around
    in the quickinstaller time after time. Too much work, so use this
    action :-) 
    """

    name = "Restart zope and call the quickreinstall script."

    def run(self):
        subActions = [StopZopeAction,
                      QuickreinstallAction,
                      StartZopeAction,
                      ]
        for actionClass in subActions:
            action = actionClass(self.conf)
            action.run()

        
class BaseZopeAction(Action):
    """Base action for starting/stopping zope
    """

    name = "Base for the zope actions."
    argument = 'start'

    def run(self):
        zopectlCommand = os.path.join(self.conf.instanceDir(), 
                                      'bin',
                                      'zopectl')
        command = ' '.join([zopectlCommand, self.argument])
        log.debug("Calling zope:")
        log.debug(command)
        os.system(command)


class StartZopeAction(BaseZopeAction):
    """Start the zope instance.
    """

    name = "Start the zope instance."
    argument = 'start'
    
    def run(self):
        BaseZopeAction.run(self)
        log.info("Started zope on port %s.",
                 self.conf.configData['port'])


class RestartZopeAction(BaseZopeAction):
    """Restart the zope instance.
    """

    name = "Restart the zope instance."
    argument = 'restart'

    def run(self):
        BaseZopeAction.run(self)
        log.info("Restarted zope on port %s.",
                 self.conf.configData['port'])


class StopZopeAction(BaseZopeAction):
    """Stop the zope instance.
    """

    name = "Stop the zope instance."
    argument = 'stop'


class QuickreinstallAction(BaseZopeAction):
    """Action that quickreinstalls your products.

    This used to depend on the presence of a specific script in your
    zope root that called the actual quickinstaller. There's a generic
    script that gets used now, however.

    For more info see the quickinstallerscript documentation.
    """

    name = "Action that quickreinstalls your products."

    def scriptLocation(self):
        """Return the location of the quickreinstall script.
        """

        ourDir = os.path.dirname(os.path.abspath(__file__))
        location = os.path.join(ourDir, config.QISCRIPT)
        log.debug("Quickinstall script location is %s.", location)
        return location

    def run(self):
        ploneSiteName = self.conf.configData['plone_site_name']
        if not ploneSiteName:
            log.debug("No plone site name, so no reinstall.")
            log.info("No quickreinstall wanted.")
            return
        reinstallScript = self.scriptLocation()
        arguments = []
        arguments.append('run') # Run a script.
        arguments.append(reinstallScript) # The script.
        # First argument: plone site name
        arguments.append(ploneSiteName)
        # Next the list of main products
        arguments += self.conf.configData['main_products']
        # Now prepare it for the BaseZopeAction.
        self.argument = ' '.join(arguments)
        log.debug("Running zopectl with these arguments: %s.",
                  self.argument)
        BaseZopeAction.run(self)
        log.info("Quick reinstall script called.")


class PrintConfigAction(Action):
    """Print the configuration.

    'instancemanager yourproject printconfig' shows the configuration
    for your project as intancemanager understands it. It will expand
    all templates, so that you can easily see the resulting values.
    """

    name = "Print the configuration for this project."

    def run(self):
        configList = self.conf.configData.keys()
        configList.sort()
        for option in configList:
            print '%s = %s' % (option, self.conf.expandTemplate(option))

class BackupZopeAction(Action):
    """Backup the Zope Database of the instance.

    This action relies on the backup_basedir_template variable to store the
    backups.
    """

    name = "Backup the instance database."

    def run(self):
        # read paths from configuration
        backup_base_dir = self.conf.backupBaseDir()
        target = os.path.join(backup_base_dir, self.conf.configData['project'])
        source = self.conf.databasePath()

        # if the backup directory doesn't exist, create it.
        if not os.path.exists(target):
            os.makedirs(target)
            log.info("%s does not exists, creating it now." % target)
        arguments = "-B -f %s -r %s" % (source, target)
        python = self.conf.configData['python']
        repozo = os.path.join(self.conf.zopeDir(), 'bin','repozo.py' )

        # make sure our software home is in the PYTHONPATH
        env={};env['PYTHONPATH']="%s/lib/python" % self.conf.zopeDir(); os.environ.update(env)
        command = ' '.join([python, repozo, arguments])
        log.info("Backing up database file: %s to %s" % (source, target))
        log.debug("Command used: %s" % command)

        os.system(command)

class RestoreZopeAction(Action):
    """Restore the Zope Database of the instance.

    This action relies on the backup_basedir_template variable to restore the
    backups from.
    """

    name = "Restore the instance database from the last available backup."

    def run(self):
        # Lets make sure zope is stopped
        action = StopZopeAction(self.conf)
        action.run()

        # read paths from configuration
        backup_base_dir = self.conf.backupBaseDir()
        source = os.path.join(backup_base_dir, self.conf.configData['project'])
        datafs = self.conf.databasePath()

        # For now only supports full restores, no point in time option.
        arguments = "-R -o %s -r %s" % (datafs, source)

        # Now we have to remove the temp files, if they exist
        for file in self.conf.databaseTempFiles():
            if os.path.exists(file):
                log.debug("Removing temporary database file: %s" % file)
                os.remove(file)

        python = self.conf.configData['python']
        repozo = os.path.join(self.conf.zopeDir(), 'bin','repozo.py' )

        # make sure our software home is in the PYTHONPATH
        env={};env['PYTHONPATH']="%s/lib/python" % self.conf.zopeDir(); os.environ.update(env)
        command = ' '.join([python, repozo, arguments])
        log.info("Restoring database file: %s from backup repository: %s" % (datafs, source))
        log.debug("Command used: %s" % command)

        os.system(command)

# User-visible actions, this allows the user to do
# 'instancemanager yourproject fresh', for instance.
ACTIONS = {
    'backup': BackupZopeAction,
    'create': CreateInstanceAction,
    'datafs': CopyDatafsAction,
    'fresh': FreshInstallAction,
    'printconfig': PrintConfigAction,
    'products': AddProductsAction,
    'restart': RestartZopeAction,
    'restore': RestoreZopeAction,
    'soft': SoftInstallAction,
    'start': StartZopeAction,
    'stop': StopZopeAction,
    #'reinstall': QuickreinstallAction,
    # Reinstall is not included as you need to stop zope first.
    # It is best to call 'soft' or 'fresh'.
    }

if __name__ == '__main__':
    # Print out documentation
    print __doc__
    print
    actionlist = list(ACTIONS.keys())
    actionlist.sort()
    for actionName in actionlist:
        action = ACTIONS[actionName]
        doc = action.__doc__
        if not doc:
            doc = action.name
        print '%s -- %s' % (actionName, doc)
        print
