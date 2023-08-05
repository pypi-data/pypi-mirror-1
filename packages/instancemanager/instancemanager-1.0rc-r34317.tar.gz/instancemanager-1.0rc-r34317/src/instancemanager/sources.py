"""The sources module handles the various sources for zope products.

 Individual product sources are sort-of wrapped by a source
 class. Product sources can be:

 * A '.tgz', '.tar', or '.zip' file.

 * A '.tgz' or '.zip' bundle.

 * A symlink (most probably to an svn directory).

 * A symlink to a bundle directory (most probably an svn bundle).
"""

import logging
import os
import os.path
import shutil
import tempfile
import utils
import urllib
log = logging.getLogger('sources')


class BaseSource(object):
    """Abstract wrapper for a source
    """

    name = 'abstractwrapper'

    def __init__(self, sourceConfig, config):
        # sourceConfig can be a dict or a string
        try:
            self.sourceName = sourceConfig.get('source')
            self.productName = sourceConfig.get('productname',
                                                self.sourceName)
            self.develop = sourceConfig.get('develop', False)
            self.drop = sourceConfig.get('droplist', ())
            self.url = sourceConfig.get('url', None)
            self.internalBundles = sourceConfig.get('internalBundles',
                                                   ())
        except AttributeError:
            self.sourceName = sourceConfig
            self.productName = os.path.basename(self.sourceName)
            self.develop = False
            self.drop = ()
            self.url = None
            self.internalBundles = ()
        if not self.sourceName:
            log.error("Failed to add %s source: '%s'.", self.name,
                      sourceConfig)
        self.config = config
        log.debug("New %s source: '%s' - develop: %s, drop: %s,"
                  " internalBundles: %s",
                  self.name, self.sourceName, self.develop, self.drop,
                  self.internalBundles)
        self.productDir = os.path.join(self.config.instanceDir(),
                                       'Products')

    def _canSafelyBeInstalled(self):
        """Return True if this product needs to be installed.
        """
        if self.config.configData['development_machine']:
            # This is a development machine, so everything can be
            # installed.
            log.debug('Product %s: development machine, so safe for install.', self.sourceName)
            return True
        if self.develop == False:
            # This Product is not specifically for development, so can
            # be safely installed.
            log.debug('Product %s: no development product, so safe for install.', self.sourceName)
            return True
        # We are on a live site and this product is for development.
        # Don't you dare install it!
        log.debug("Product %s: development product on "
                  "non-development machine, so NOT safe for install.",
                  self.sourceName)
        return False

    def _attemptDownload(self):
        """Overwrite in subclass.
        """

        pass

    def _source(self):
        """Return the absolute source path.
        """

        if self.sourceName is None:
            return ''
        methodName = self.name + 'BaseDir'
        method = getattr(self.config, methodName)
        baseDir = method()
        absoluteSourcePath = os.path.join(baseDir, self.sourceName)
        return absoluteSourcePath

    def removeTargetIfExists(self, target):
        """If the target file/dir exists, remove it.
        """

        if os.path.exists(target):
            if target.lower().endswith('.txt'):
                # Don't bug anyone about a duplicate EXTERNALS.txt or
                # so.
                log.debug("%s is a .txt file, silently removing "
                          "it without warning.")
            else:
                log.warn("'%s' exists, removing it before using %s on %s.",
                         target, self.name, self.sourceName)
            # a symlink to a directory is also a directory.
            if os.path.islink(target):
                os.remove(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)

    def addProduct(self, manifest=None):
        """Add a product.  

        This only checks if the source for that product exists.
        Override this method in child classes and call this method
        there.
        """

        source = self._source()
        self.manifest=manifest
        if not os.path.exists(source):
            if self.url:
                self._attemptDownload()
        if not os.path.exists(source):
            log.warn('Product %s not found.', source)
            raise IOError
        if self._canSafelyBeInstalled():
            log.debug('Product %s is safe for install.', source)
            self._addProduct()
        else:
            log.info('Not installing product %s as it is not meant for live sites.', source)
        
    def _buildManifest(self, nestedSource, target):
        manifest=self.manifest
        if manifest is None:
            return
        if target.lower().endswith('.txt'):
            return    
        #extend the trace information - time ordered
        trace=manifest.setdefault('trace', [])
        try:
            version=open(os.path.join(target, 'version.txt')).readline().strip()
        except:
            version=" - "
        item=(self.name, self._source(), nestedSource, target, version)
        trace.append(item)
        #extend a dict of what products are installed:
        installed=manifest.setdefault('installed', {})
        prodname=os.path.split(target)[1]
        sources=installed.setdefault(prodname,[])
        sources.append(self._source() + ':' + version)
        

class SymlinkSource(BaseSource):
    """Wrapper around a symlink source.
    """

    name = 'symlink'

    def _addProduct(self):
        source = self._source()
        target = os.path.join(self.productDir, self.productName)
        self.removeTargetIfExists(target)
        utils.symlink(source, target, self.config)
        log.debug("Symlink added '%s'=>'%s'.", target, source)
        self._buildManifest(None, target)

    def _attemptDownload(self):
        if not self.url:
            return
        target = self._source()
        log.info("Checking out %s ...", target)
        command = 'svn checkout %s %s' % (self.url, target)
        log.debug('commandline: %s', command)
        os.system(command)
        log.info("Checked out from %s.", self.url)
        pass

class SymlinkbundleSource(SymlinkSource):
    """Wrapper around a symlink bundle source.
    """

    name = 'symlinkbundle'

    def _addProduct(self):
        source = self._source()
        includedFiles = os.listdir(source)
        # Filter out .svn
        includedFiles = [f for f in includedFiles
                         if not f.startswith('.')]
        log.debug("Found this in the symlink bundle dir: %r.",
                  includedFiles)
        for includedFile in includedFiles:
            if includedFile.endswith('.OLD'):
                log.warn("Svn .OLD file, not linking it: %s.",
                         includedFile)
                continue
            if includedFile in self.drop:
                log.warn("file %s in droplist, not linking it.",
                         includedFile)
                continue
            newSource = os.path.join(source, includedFile)
            target = os.path.join(self.productDir, includedFile)
            self.removeTargetIfExists(target)
            utils.symlink(newSource, target, self.config)
            log.debug("Symlink added '%s'=>'%s'.", target, newSource)
            self._buildManifest(newSource, target)


class ArchiveSource(BaseSource):
    """Wrapper around an archive source.
    """

    name = 'archive'

    def _attemptDownload(self):
        if not self.url:
            return
        target = self._source()
        log.info("Downloading %s ...", target)
        urllib.urlretrieve(self.url, target)
        log.info("Downloaded from %s.", self.url)

    def moveDirs(self, tempDir):
        try:
            extractedDirectory = os.listdir(tempDir)[0]
            target = os.path.join(self.productDir, extractedDirectory)
            self.removeTargetIfExists(target)
            if extractedDirectory in self.drop:
                log.warn("Directory %s in droplist for %s, not installing it." %
                         (extractedDirectory, self.sourceName))
                return
            shutil.move(extractedDirectory, target)
            self._buildManifest(None, target)
        except IndexError:
            log.warn('Product %s not found in %s', 
                     self.sourceName,
                     tempDir) 

    def _addProduct(self):
        source = self._source()
        # Extract zip in temp directory
        tempDir = tempfile.mkdtemp()
        currentDir = os.getcwd()
        log.debug("Extracting into '%s'.", tempDir)
        os.chdir(tempDir)
        utils.adaptiveUnarchive(source)
        # Move resulting directory|ies to target
        self.moveDirs(tempDir)
        # Remove temp directory
        os.chdir(currentDir)
        shutil.rmtree(tempDir)
        log.debug("Archive extracted '%s'.", source)


class ArchivebundleSource(ArchiveSource):
    """Wrapper around an archive bundle bundle.
    """

    name = 'archivebundle'

    def moveDirs(self, tempDir):
        extractedDirectories = os.listdir(tempDir)
        log.debug("Extracted dirs: %r.", extractedDirectories)
        if len(extractedDirectories) ==  1:
            log.debug("One nice neat directory extracted, "
                      "moving its contents.")
            bundleDir = os.path.join(tempDir,
                                     extractedDirectories[0])
            os.chdir(bundleDir)
            extractedDirectories = os.listdir(bundleDir)
            log.debug("New extracted dirs: %r.", extractedDirectories)        
        for extractedDirectory in extractedDirectories:
            target = os.path.join(self.productDir, extractedDirectory)
            self.removeTargetIfExists(target)
            if extractedDirectory in self.drop:
                log.warn("Directory %s in droplist for %s, not installing it." %
                         (extractedDirectory, self.sourceName))
                continue
            if extractedDirectory in self.internalBundles:
                log.debug("Moving the contents of %s one level up.",
                          extractedDirectory)
                localDirs = os.listdir(extractedDirectory)
                for localDir in localDirs:
                    target = os.path.join(self.productDir, localDir)
                    self.removeTargetIfExists(target)
                    source = os.path.join(extractedDirectory,
                                          localDir)
                    shutil.move(source, target)
                    log.debug("Moved %s.", localDir)
                    self._buildManifest(localDir, target)
                continue
            shutil.move(extractedDirectory, target)
            log.debug("Moved %s.", extractedDirectory)
            self._buildManifest(extractedDirectory, target)
            


