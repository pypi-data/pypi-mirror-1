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
log = logging.getLogger('sources')


class BaseSource(object):
    """Abstract wrapper for a source
    """

    name = 'abstractwrapper'

    def __init__(self, sourceName, config):
        self.sourceName = sourceName
        self.config = config
        log.debug("New %s source: '%s'.", self.name, sourceName)
        self.productDir = os.path.join(self.config.instanceDir(),
                                       'Products')

    def _source(self):
        """Return the absolute source path.
        """

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
                log.warn("'%s' exists, removing it before using %s.",
                         target, self.name)
            # a symlink to a directory is also a directory.
            if os.path.islink(target):
                os.remove(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)

    def addProduct(self):
        """Add a product.  

        This only checks if the source for that product exists.
        Override this method in child classes and call this method
        there.
        """

        source = self._source()
        if not os.path.exists(source):
            log.warn('Product %s not found.', source)
            raise IOError


class SymlinkSource(BaseSource):
    """Wrapper around a symlink source.
    """

    name = 'symlink'

    def addProduct(self):
        super(SymlinkSource, self).addProduct()
        productName = os.path.basename(self.sourceName)
        source = self._source()
        target = os.path.join(self.productDir, productName)
        self.removeTargetIfExists(target)
        utils.symlink(source, target, self.config)
        log.debug("Symlink added '%s'=>'%s'.", target, source)


class SymlinkbundleSource(BaseSource):
    """Wrapper around a symlink bundle source.
    """

    name = 'symlinkbundle'

    def addProduct(self):
        super(SymlinkbundleSource, self).addProduct()
        source = self._source()
        includedFiles = os.listdir(source)
        # Filter out .svn
        includedFiles = [f for f in includedFiles
                         if not f.startswith('.')]
        log.debug("Found this in the symlink bundle dir: %r.",
                  includedFiles)
        for includedFile in includedFiles:
            newSource = os.path.join(source, includedFile)
            target = os.path.join(self.productDir, includedFile)
            self.removeTargetIfExists(target)
            utils.symlink(newSource, target, self.config)
            log.debug("Symlink added '%s'=>'%s'.", target, newSource)


class ArchiveSource(BaseSource):
    """Wrapper around an archive source.
    """

    name = 'archive'

    def moveDirs(self, tempDir):
        try:
            extractedDirectory = os.listdir(tempDir)[0]
            target = os.path.join(self.productDir, extractedDirectory)
            self.removeTargetIfExists(target)
            shutil.move(extractedDirectory, target)
        except IndexError:
            log.warn('Product %s not found in %s', self.sourceName, tempDir)

    def addProduct(self):
        super(ArchiveSource, self).addProduct()
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
    """Wrapper around a archive bundle bundle.
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
            shutil.move(extractedDirectory, target)
            log.debug("Moved %s.", extractedDirectory)


