"""Actions that can be performed on instances and products.


 Everything that is handy to have as a single unit of action is turned
 into an Action. They can be quite small (just stopping zope), but
 that's OK. Being able to say 'instancemanager myproject stop' from
 anywhere without having to go to the instance directory to say
 'bin/zopectl stop' saves on the number of terminals you have to keep
 open.

"""

import actionutils
import config
import logging
import os
import os.path
import shutil
import sys
import tempfile
from actionutils import InvokedInVolatileDir
log = logging.getLogger('actions')

class Action:
    """Base class for all actions.

    name -- The short name used in the optionparser's help message.

    option -- Option string like '--option', if not present (like in
    this base class), it will not be turned into an option.
    """

    name = 'abstract base action'
    option = None
    alternativeOption = None
    kindOfAction = 'store_true'

    def __init__(self, configuration):
        self.conf = configuration

    def run(self, options=None):
        pass

    def addOption(self, optionparser):
        optionparser.add_option(
            self.option,
            self.alternativeOption,
            help=self.name,
            action=self.kindOfAction,
            default=False)

class ArgumentAction(Action):
    """Base action that accepts one parameter.

    The normal actions are only switched on (default is off), this
    action accepts additional parameters.
    """

    kindOfAction = 'store' #TODO
    metavar = 'CMD'

    def addOption(self, optionparser):
        optionparser.add_option(
            self.option,
            self.alternativeOption,
            help=self.name,
            metavar=self.metavar,
            action=self.kindOfAction)


class CreateInstanceAction(Action):
    """Create a zope instance, possibly including a zeo server.

    This will create a zope instance for you using the familiar
    'mkzopeinstance' command. The instance will be the location you
    specified in your config file. By default it will be
    '~/instances/projectname/'.

    Also, the zope.conf will be adapted in some places, like enabling
    debug mode and verbose security (for zope 2.8 and up). The port,
    username and password will be set according to the config file.
    """

    name = "Create a zope instance for your project."
    option = '--create'

    def run(self, options=None):
        # We want to reuse this method in another action
        #
        actionutils.createInstance(self.conf, purge=True)


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
    option = '--copydatafs'

    def run(self, options=None):
        source = self.conf.datafs()
        # databasepath keeps track of zeo usage
        target = self.conf.databasePath()
        if not os.path.exists(source):
            log.info("No prepared Data.fs found at %s, "
                     "skipping this step.", source)
            return
        else:
            log.info("Copying over fresh Data.fs from %s.", source)
            shutil.copy(source, target)
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
    option = '--products'

    def _manMsg(self, msg):
        """allow easy redirect of manifest messages"""
        log.info(msg)

    def _commonLeft(self, common, item):
        "returns the common string starting left"
        a, b = common, item
        c=''
        if b == None:
            return a
        for i in range(len(a)):
            #run off the end of b?
            if i>=len(b):
                return c
            #always prefer to keep a path if we have one
            if a.startswith('/') and not b.startswith('/'):
                return a
            if a[i] != b[i]:
                return c
            c+=a[i]
        return c

    def _snipCommon(self, common, s):
        """snip off the common string from s"""
        #if there's nothing common - return s
        if not common:
            return s
        #sometimes s is None
        if not s:
            return ''
        # if we snip, say so by putting a +
        return s.replace(common, '+')

    MANFORMAT="%26s : %s"
    MANITEM= "%14s %48s %38s %48s %-20s"
    cc='='
    MANLINES=(cc*14, cc*48, cc*38, cc*48, cc*20)
    MANTITLE=('type', 'source', 'nested source', 'target', 'version')
    def _printManifest(self, manifest):
        #show the installation sequence
        item = manifest['trace'][0]
        common=[item[ind] for ind in range(len(item))]
        for item in manifest['trace']:
            for i in (range(len(item))):
                c=self._commonLeft(common[i], item[i])
                common[i:i+1]=[c]
        self._manMsg( self.MANITEM % self.MANLINES )
        self._manMsg( self.MANITEM % self.MANTITLE )
        headings=[]
        for c in common:
            if c:
                headings.append(c+'+')
            else:
                headings.append('')
        self._manMsg( self.MANITEM % tuple(headings) )
        self._manMsg( self.MANITEM % self.MANLINES )
        for item in manifest['trace']:
            it=[self._snipCommon(common[i], item[i]) for i in range(len(item))]
            it[4:5]=[it[4][0:20]]
            self._manMsg(self.MANITEM % tuple(it))
        #show what's actually installed
        installed = manifest['installed'].items()
        installed.sort()
        self._manMsg('')
        self._manMsg('-'*170)
        self._manMsg('Duplicates, and their sources...')
        self._manMsg('-'*170)
        dupe=False
        for product, attempts in installed:
            if len(attempts) > 1:
                p=product
                dupe=True
                for attempt in attempts:
                    self._manMsg(self.MANFORMAT % (p, attempt))
                    p=' '
        if not dupe:
            self._manMsg('None found')
        self._manMsg('='*170)

    def run(self, options=None):
        instanceDirs = self.conf.zeoClientDirs()
        # Make sure our current directory is not any of the zope
        # instances.
        for instanceDir in instanceDirs:
            try:
                actionutils.trapUsageWithinVolatileDir(instanceDir)
            except InvokedInVolatileDir, error:
                log.error(error)
                sys.exit(1)

        # Rebuild the products dir for the first zope.
        instanceDir = instanceDirs[0]
        target = os.path.join(instanceDir, 'Products')
        log.info("Removing %s...", target)
        shutil.rmtree(target)
        log.info("Removed the entire %s directory.", target)
        os.mkdir(target)
        log.debug("Created it again.")
        log.info("Adding Products...")
        manifest={}
        for source in self.conf.sources(instanceDir):
            try:
                source.addProduct(manifest)
            except IOError:
                # XXX Maybe we want to quit with an error here.        
                log.warn('Please fix this.')
        log.info("Rebuilt the %s/Products/ directory from scratch.",
                 instanceDir)

        # In case of multiple zeo clients, simply copy the Products
        # dir from the first client.  This at least gains us time when
        # the Products dir is built with an svn export.
        firstZopeProductsDir = target
        for instanceDir in instanceDirs[1:]:
            target = os.path.join(instanceDir, 'Products')
            shutil.rmtree(target)
            shutil.copytree(firstZopeProductsDir, target, symlinks=True)

        # Only print the manifest for the first instance.
        if options and options.manifest:
            self._printManifest(manifest)

class ZopectlAction(ArgumentAction):
    """Action for calling zopectl.
    """

    name = "Runs your instance's 'bin/zopectl CMD'."
    option = '--zope'
    alternativeOption = '-z'

    def run(self, options=None):
        command = options.zope
        actionutils.runZopectl(self.conf, command)


class TestAction(ArgumentAction):
    """Action for calling zopectl with a test command.
    """

    name = "Runs tests for product PRD (use ALL for all products)."
    metavar = 'PRD'
    option = '--test'
    alternativeOption = '-t'

    def zopeVersion(self):
        """Return first two numbers of the zope version.

        So '28' for zope 2.8, '29' for zope 2.9.3.
        """

        version = self.conf.configData['zope_version']
        version = version.replace('.', '')
        return version[:2]

    def testCommand(self, product):
        arguments = []
        arguments.append('test')
        version = self.zopeVersion()
        template_29 = '-s Products.%s'
        # in case of zeo, using the first zeo client is fine here.
        template_27 = '--libdir ' + self.conf.instanceDir() + '/Products/%s'
        template = template_29
        if version in ['27', '28']:
            template = template_27
        if not product == 'ALL':
            arguments.append(template % product)
        command = ' '.join(arguments)
        return command

    def run(self, options=None):
        product = options.test
        command = self.testCommand(product)
        actionutils.runZopectl(self.conf, command)


class ZeoctlAction(ArgumentAction):
    """Action for calling zeoctl.
    """

    name = "Runs your zeo server's 'bin/zeoctl CMD'."
    option = '--zeo'

    def run(self, options=None):
        command = options.zeo
        actionutils.runZeoctl(self.conf, command)

class RunCommandAction(Action):
    """ Run external command action

    This action calls external script using os.system call
    Script is called for all instanceDirs.
    """

    name = "Run external command."
    option = '--runcommand'

    def run(self, options=None):
        instanceDirs = self.conf.zeoClientDirs()
        for instanceDir in instanceDirs:
            actionutils.runCommand(self.conf, instanceDir)
            

class QuickreinstallAction(Action):
    """Action that quickreinstalls your products.

    This used to depend on the presence of a specific script in your
    zope root that called the actual quickinstaller. There's a generic
    script that gets used now, however.

    For more info see the quickinstallerscript documentation.
    """

    name = "Action that quickreinstalls your products."
    option = '--reinstall'
    alternativeOption = '-r'

    def scriptLocation(self):
        """Return the location of the quickreinstall script.
        """

        ourDir = os.path.dirname(os.path.abspath(__file__))
        location = os.path.join(ourDir, config.QISCRIPT)
        log.debug("Quickinstall script location is %s.", location)
        return location

    def run(self, options=None):
        ploneSiteName = self.conf.configData['plone_site_name']
        adminUser = self.conf.configData['user']
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
        # Second argument: id of admin user who creates the plone site
        arguments.append(adminUser)
        # Next the list of main products
        arguments += actionutils.adaptListForDevelopment( self.conf,
            self.conf.configData['main_products'])
        # and the GenericSetup profiles
        arguments += actionutils.adaptListForDevelopment( self.conf,
            self.conf.configData['generic_setup_profiles'])

        # Now prepare it for the BaseZopeAction.
        command = ' '.join(arguments)
        actionutils.runZopectl(self.conf, command)
        log.info("Quick reinstall script called.")

class UninstallAction(ArgumentAction):
    """Action that uninstalls a given product from your instance.
    """

    name = "Action that uninstalls a given product"
    option = '--uninstall'
    alternativeOption = '-u'

    def scriptLocation(self):
        """Return the location of the uninstall script.
        """

        ourDir = os.path.dirname(os.path.abspath(__file__))
        location = os.path.join(ourDir, config.UISCRIPT)
        log.debug("Uninstall script location is %s.", location)
        return location

    def run(self, options=None):
        product = options.uninstall
        ploneSiteName = self.conf.configData['plone_site_name']
        adminUser = self.conf.configData['user']
        if not ploneSiteName:
            log.debug("No plone site name, so no uninstall.")
            log.info("No uninstall wanted.")
            return
        uninstallScript = self.scriptLocation()
        arguments = []
        arguments.append('run') # Run a script.
        arguments.append(uninstallScript) # The script.
        # First argument: plone site name
        arguments.append(ploneSiteName)
        # Second argument: id of admin user who creates the plone site
        arguments.append(adminUser)
        # Next the product
        arguments.append(product)

        # Now prepare it for the BaseZopeAction.
        command = ' '.join(arguments)
        actionutils.runZopectl(self.conf, command)
        log.info("Quick uninstall script called.")


class UpgradeZopeAction(Action):
    """ Copies over the zope.conf or regenerates it based on the current
        configuration and copies over the zopectl from the correct skeleton.
        Upgrade your instance in 2 steps:

        1. Update the Zope version in your project.py
        2. run instancemanager --upgradezope
    """

    name = "Update the zope.conf used for your instance"
    option = '--upgradezope'

    def run(self, options=None):
        # update the executables by deleting them from the instance and then
        # running mkzopeinstance.py again. Also zope.conf is refreshed
        useZeo = self.conf.configData['use_zeo']
        python = self.conf.configData['python']
        instanceDirs = self.conf.zeoClientDirs()
        filesnames = ['zopectl', 'runzope', 'zopeservice.py', 'runzope.bat']
        files = []
        for instanceDir in instanceDirs:
            for name in filesnames:
                files.append((os.path.join(instanceDir, 'bin', name)))
            files.append(os.path.join(instanceDir, 'etc','zope.conf'))
        if useZeo:
            zeoDir = self.conf.zeoDir()
            files.append(os.path.join(zeoDir, 'bin', 'zeoctl'))
            files.append(os.path.join(zeoDir, 'bin', 'runzeo'))
            files.append(os.path.join(zeoDir, 'etc', 'zeo.conf'))
        for f in files:
            if os.path.exists(f):
                shutil.os.remove(f)
                log.debug("Removed %s" % f)
        actionutils.createInstance(self.conf, purge=False)


class PackAction(Action):
    """Action that packs your database.
    """

    name = "Action that packs your database."
    option = '--pack'

    def scriptLocation(self):
        """Return the location of the pack script.
        """

        ourDir = os.path.dirname(os.path.abspath(__file__))
        location = os.path.join(ourDir, config.PACKSCRIPT)
        log.debug("Pack script location is %s.", location)
        return location

    def run(self, options=None):
        days = self.conf.configData['pack_days']
        if not self.conf.configData['use_zeo']:
            # This should be okay for zeo as well.  But at least
            # *without* zeo the pack just fails if you do it with the
            # pack script.
            os.system('wget -q http://%(user)s:%(password)s@localhost:%(port)s/Control_Panel/Database/manage_pack?days:float=%(pack_days)s' % self.conf.configData)
            log.info("Database Pack called.")
        else:
            # Instead of this, we could also call the bin/zeopack.py
            # script that is in the Zope source.
            # But that is something for another day.
            packScript = self.scriptLocation()
            arguments = []
            arguments.append('run') # Run a script.
            arguments.append(packScript) # The script.
            # Argument: the number of days to leave unpacked.
            arguments += days
            command = ' '.join(arguments)
            actionutils.runZopectl(self.conf, command)
            log.info("Pack script called.")


class ChangeOwnershipAction(Action):
    """Action that changes ownership of some documents.
    """

    name = "Action that changes ownership of some documents."
    option = '--changeown'

    def scriptLocation(self):
        """Return the location of the pack script.
        """

        ourDir = os.path.dirname(os.path.abspath(__file__))
        location = os.path.join(ourDir, config.CHANGEOWNSCRIPT)
        log.debug("Change ownership script location is %s.", location)
        return location

    def run(self, options=None):
        changeownScript = self.scriptLocation()

        arguments = []
        arguments.append('run') # Run a script.
        arguments.append(changeownScript) # The script.
        # First argument: plone site name
        ploneSiteName = self.conf.configData['plone_site_name']
        arguments.append(ploneSiteName)
        # Argument: the original owner
        arguments.append('all_powerful_Oz')
        # Argument: the new owner
        adminUser = self.conf.configData['user']
        arguments.append(adminUser)
        command = ' '.join(arguments)
        actionutils.runZopectl(self.conf, command)
        log.info("Change ownership script called.")


class PrintConfigAction(Action):
    """Print the configuration.

    'instancemanager yourproject printconfig' shows the configuration
    for your project as intancemanager understands it. It will expand
    all templates, so that you can easily see the resulting values.
    """

    name = "Print the configuration for this project."
    option = '--printconfig'

    def run(self, options=None):
        configList = self.conf.configData.keys()
        configList.sort()
        for option in configList:
            print '%s = %s' % (option, self.conf.expandTemplate(option))

class BackupZopeAction(Action):
    """Backup the Zope Database of the instance.

    This action relies on the backup_basedir_template variable to store the
    backups. By default, the backups are incremental unless there's
    been a pack.
    """

    name = "Backup the instance database (incremental backup)."
    option = '--backup'
    alternativeOption = '-b'

    def run(self, options=None):
        # read paths from configuration
        target = self.conf.backupBaseDir()
        source = self.conf.databasePath()
        actionutils.backup(conf=self.conf,
                           sourceDatafs=source,
                           targetDir=target,
                           full=False)

class RepozoAction(ArgumentAction):
    """Perform a variety of repozo backup/restore actions.

    --backup and --restore are fine, but there are more diverse things
    that can be done with repozo, this action allows some of them.
    """

    name = "Other backup/restore tasks with repozo."
    option = '--repozo'
    choices = ['sync',
               'snapshot',
               'restoresnapshot',
               'full',
               ]

    def addOption(self, optionparser):
        optionparser.add_option(
            self.option,
            self.alternativeOption,
            help=self.name,
            action=self.kindOfAction,
            default=False,
            choices=self.choices)

    def run(self, options=None):
        choice = options.repozo
        methodToRun = getattr(self, choice)
        methodToRun(options)

    def full(self, options=None):
        # read paths from configuration
        target = self.conf.backupBaseDir()
        source = self.conf.databasePath()
        actionutils.backup(conf=self.conf,
                           sourceDatafs=source,
                           targetDir=target,
                           full=True)

    def snapshot(self, options=None):
        # read paths from configuration
        target = self.conf.snapshotBaseDir()
        source = self.conf.databasePath()
        actionutils.backup(conf=self.conf,
                           sourceDatafs=source,
                           targetDir=target,
                           full=True)

    def restoresnapshot(self, options=None):
        sourceDir = self.conf.snapshotBaseDir()
        actionutils.restore(conf=self.conf,
                            sourceDir=sourceDir)

    def sync(self, options=None):
        syncDatabase = self.conf.configData['sync_database']
        if not syncDatabase:
            log.warn("No sync_database specified, not syncing.")
            return
        log.debug("Syncing databases...")
        # Create tempdir.
        tempDir = tempfile.mkdtemp()
        log.debug("Using tempdir %s.", tempDir)
        # Make full backup of the source database.
        source = syncDatabase
        target = tempDir
        actionutils.backup(conf=self.conf,
                           sourceDatafs=source,
                           targetDir=target,
                           full=True)
        # Restore that backup to the target.
        sourceDir = tempDir
        actionutils.restore(conf=self.conf,
                            sourceDir=sourceDir)
        # Zap the tempdir.
        shutil.rmtree(tempDir)


class RestoreZopeAction(Action):
    """Restore the Zope Database of the instance.

    This action relies on the backup_basedir_template variable to restore the
    backups from.
    """

    name = "Restore the database from the regular backup."
    option = '--restore'

    def run(self, options=None):
        # read paths from configuration
        sourceDir = self.conf.backupBaseDir()
        actionutils.restore(conf=self.conf,
                            sourceDir=sourceDir)


class RestoreDateZopeAction(ArgumentAction):
    """Restore the Zope Database of the instance by date

    This action relies on the backup_basedir_template variable to restore the
    backups from.
    """

    name = "Restore situation at DATE from regular backup."
    option = '--restore-date'
    metavar = 'DATE'

    def run(self, options=None):
        # read paths from configuration
        sourceDir = self.conf.backupBaseDir()
        fromTime = options.restore_date
        actionutils.restore(conf=self.conf,
                            sourceDir=sourceDir,
                            fromTime=fromTime)


class RewriteruleAction(Action):
    """Print out a RewriteRule for use in your apache config.

    Also include some helpful pointers to information.
    """

    name = "Print out an apache rewriterule."
    option = '--rewriterule'

    def run(self, options=None):
        ploneSiteName = self.conf.configData['plone_site_name']
        zopePort = self.conf.instancePort()
        sn = '%{SERVER_NAME}' # This hoses the template :-)
        output = config.APACHE_TEMPLATE % {
            'plonesite': ploneSiteName,
            'zopeport': zopePort,
            'sn': sn}
        print output


def getActions():
    """Return a list of action classes in this module.
    """

    moduleContents = globals()
    actions = [moduleContents[key] for key in moduleContents.keys()
               if key.endswith('Action')]
    actions = [action for action in actions
               if action.option]
    def customSort(x, y):
        return cmp(x.option, y.option)
    actions.sort(customSort)
    return actions

def addOptions(optionparser):
    for Action in getActions():
        tempInstance = Action(None)
        tempInstance.addOption(optionparser)


if __name__ == '__main__':
    # Print out documentation
    print __doc__
    print
    for action in getActions():
        doc = action.__doc__
        if not doc:
            doc = action.name
        print "'%s' -- %s" % (action.option, doc)
        print

