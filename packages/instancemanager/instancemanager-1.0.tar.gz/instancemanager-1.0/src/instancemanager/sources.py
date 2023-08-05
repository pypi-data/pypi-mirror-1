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
import sys
import tempfile
import utils
import urllib
try:
    import pysvn
    USE_PYSVN = True
except:
    USE_PYSVN = False
log = logging.getLogger('sources')


def sourceNameFromUrl(url):
    """Return guessed source name from svn url.

    Normally, this is the last part of the path.

      >>> sourceNameFromUrl('https://svn/test/something')
      'something'

    If it isn't something we recognize (which means 'starts with
    https://', for instance), just leave it alone.

      >>> sourceNameFromUrl('test')
      'test'
      >>> sourceNameFromUrl('some/cvs -r1234 strange stuff')
      'some/cvs -r1234 strange stuff'
      >>> sourceNameFromUrl('urgh://svn/test/branches/someting')
      'urgh://svn/test/branches/someting'

    Strip off '/trunk' as that is always OK.

      >>> sourceNameFromUrl('https://svn/test/trunk')
      'test'

    Strip off '/tags/something' and 'branches/something' as that is
    almost always OK. Just fill in the sourceName if that isn't the
    right choice :-)

      >>> sourceNameFromUrl('https://svn/test/branches/someting')
      'test'
      >>> sourceNameFromUrl('https://svn/test/tags/someting')
      'test'

    Keep not-exact matches intact, like branches with two sublevels or
    other strange things. Just return the last part.

      >>> sourceNameFromUrl('https://svn/test/trunk/something')
      'something'
      >>> sourceNameFromUrl('https://svn/test/branches/some/thing')
      'thing'

    But beware of zip files (that also start with http). In those
    cases, also just return the last part of the url.

      >>> sourceNameFromUrl('https://svn/test.tgz')
      'test.tgz'
      >>> sourceNameFromUrl('https://svn/test.tar.gz')
      'test.tar.gz'
      >>> sourceNameFromUrl('https://svn/test.zip')
      'test.zip'


    """

    log.debug("Extracting source name from string %r by checking "
              "if it is a url and thus needs special treatment.", url)
    parts = url.split('/')
    if len(parts) < 2:
        # Safety valve.
        log.debug("No slash in the name, so no url: returning as-is.")
        return url
    svnIndicators = ['http', # This also covers https.
                     'svn']
    weRecognizeIt = False
    for indicator in svnIndicators:
        if url.startswith(indicator):
            log.debug("String starts with %r, possible url.",
                      indicator)
            weRecognizeIt = True
    if not weRecognizeIt:
        log.debug("No url recognized, returning as-is.")
        return url
    zipIndicators = ['zip', 'gz']
    for indicator in zipIndicators:
        if url.endswith(indicator):
            result = parts[-1]
            log.debug("Possible zipfile (it ends with %r), returning "
                      "the last part: %r.", indicator, result)
            return result
    log.debug("We checked, it doesn't seem to be a "
              "zipfile. Continuing.")
    if parts[-1] == 'trunk':
        result = parts[-2]
        log.debug("It ends with '/trunk', returning part before "
                  "that: %r.", result)
        return result
    if parts[-2] in ['tags', 'branches']:
        result = parts[-3]
        lastPart = '/'.join(parts[-2:])
        log.debug("It ends with %r, so returning part before "
                  "that: %r.", lastPart, result)
        return result
    # Nothing special matched yet, so just return the last part.
    return parts[-1]

class BaseSource(object):
    """Abstract wrapper for a source
    """

    name = 'abstractwrapper'

    def __init__(self, sourceConfig, config, instanceDir):
        # sourceConfig can be a dict or a string
        if type(sourceConfig) == type(dict()):
            log.debug("Source config is a dict, grabbing data.")
            self.develop = sourceConfig.get('develop', False)
            self.drop = sourceConfig.get('droplist', ())
            self.url = sourceConfig.get('url', None)
            self.usecvs = sourceConfig.get('use_cvs', None)
            self.version = sourceConfig.get('version', None)
            self.sourceName = sourceConfig.get('source', None)
            self.deleteExisting = sourceConfig.get('deleteExisting',
                                                   True)
            if self.sourceName is None and self.url is not None:
                self.sourceName =  sourceNameFromUrl(self.url)
            if self.sourceName is None:
                log.critical('Cannot find a "source" key nor a '
                             '"url" key, so I cannot deduct a source '
                             'name. (%r).', sourceConfig)
                sys.exit(1)
            self.productName = sourceConfig.get('productname',
                                                self.sourceName)
            self.userdefinedProductName = sourceConfig.get('productname', None)
            self.pylib = sourceConfig.get('pylib', False)
            self.instanceBundle = sourceConfig.get('instancebundle', False)
            self.internalBundles = sourceConfig.get('internalBundles',())
        if type(sourceConfig) == type(''):
            log.debug("Source config is a string (%s).", sourceConfig)
            self.sourceName = sourceConfig
            self.url = None
            self.sourceName = sourceNameFromUrl(sourceConfig)
            if self.sourceName != sourceConfig:
                log.debug("We could extract a url from the "
                          "sourceconfig. Now we'll set the url "
                          "with the original value.")
                self.url = sourceConfig
                log.debug("Source name set to %r, url to %r.",
                          self.sourceName, self.url)
            self.productName = os.path.basename(self.sourceName)
            self.develop = False
            self.drop = ()
            self.usecvs = None
            self.version = None
            self.pylib = False
            self.internalBundles = ()
            self.deleteExisting = True
            self.userdefinedProductName = None
        if not self.sourceName:
            log.error("Failed to add %s source: '%s'.", self.name,
                      sourceConfig)
        self.config = config
        self.sourceConfig = sourceConfig
        log.debug("New %s source: '%s' - develop: %s, drop: %s,"
                  " internalBundles: %s",
                  self.name, self.sourceName, self.develop, self.drop,
                  self.internalBundles)
        self.instanceDir = instanceDir
        self.productDir = os.path.join(instanceDir, 'Products')
        self.libDir = os.path.join(instanceDir, 'lib', 'python')

    def _canSafelyBeInstalled(self):
        """Return True if this product needs to be installed.
        """

        if self.config.configData['development_machine']:
            # This is a development machine, so everything can be
            # installed.
            log.debug('Product %s: development machine, '
                      'so safe for install.', self.sourceName)
            return True
        if self.develop == False:
            # This Product is not specifically for development, so can
            # be safely installed.
            log.debug('Product %s: no development product, '
                      'so safe for install.', self.sourceName)
            return True
        # We are on a live site and this product is for development.
        # Don't you dare install it!
        log.debug("Product %s: development product on "
                  "non-development machine, so NOT safe for install.",
                  self.sourceName)
        return False

    def attemptDownload(self):
        """Overwrite in subclass.
        """

        pass

    def _source(self):
        """Return the absolute source path.
        """

        methodName = self.name + 'BaseDir'
        method = getattr(self.config, methodName)
        baseDir = method()
        absoluteSourcePath = os.path.join(baseDir, self.sourceName)
        return absoluteSourcePath

    def _removeTarget(self, target):
        """Remove the target.
        """

        if target.lower().endswith('.txt'):
            # Don't bug anyone about a duplicate EXTERNALS.txt or
            # so.
            log.debug("%s is a .txt file, silently removing "
                      "it without warning.")
        else:
            log.info("'%s' exists, removing it before using %s from %s.",
                     target, self.name, self.sourceName)
        # a symlink to a directory is also a directory.
        if os.path.islink(target):
            os.remove(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)

    def prepareInstall(self, target):
        """Return True if the target preparation was successful.

        Unsuccessful can mean that there is an existing product that
        should not be deleted.
        """

        if not os.path.exists(target):
            log.debug("%s doesn't exist, go ahead with an install.",
                      target)
            return True
        if self.deleteExisting:
            self._removeTarget(target)
            log.debug("Target %s removed, go ahead with an install.",
                      target)
            return True
        log.debug("Target %s exists and we're not supposed to delete "
                  "it, stop the install of this one.", target)
        return False

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
                self.attemptDownload()
        if self._canSafelyBeInstalled():
            log.debug('Product %s is safe for install.', source)
            if not os.path.exists(source):
                log.warn('Product %s not found.', source)
                raise IOError
            self._addProduct()
        else:
            log.info('Not installing product %s as it is not meant for live sites.', source)

    def updateSource(self, manifest=None):
        """Update the source of a product.

        This action will call the _updateSource method in the child classes.
        """
        source = self._source()
        self.manifest=manifest
        if not os.path.exists(source):
            if self.url:
                log.warn('Source %s not found, attempting download.',
                         source)
                self.attemptDownload()
            else:
                log.critical("Source %s not found, also no url "
                             "where to download it.", source)
                sys.exit(1)
        else:
            self._updateSource()

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
        if self.pylib:
            target = os.path.join(self.libDir, self.productName)
        else:
            target = os.path.join(self.productDir, self.productName)
        if self.prepareInstall(target):
            utils.symlink(source, target, self.config)
            self._buildManifest(None, target)

    def _updateSource(self):
        if not self.url:
            log.info("No svn/cvs url set for source %s. "
                     "Attempting an update anyway, it might be part "
                     "of a bundle, for instance. Errors are ok here.",
                     self.sourceName)
        target = self._source()
        versionoption = self.version and "-r %s" % self.version or ""
        # svn + pysvn
        if USE_PYSVN and not self.usecvs:
            client = pysvn.Client()
            try:
                revisionnumber = (
                    self.version and
                    pysvn.Revision(pysvn.opt_revision_kind.number,
                                   self.version) or
                    pysvn.Revision(pysvn.opt_revision_kind.head))
                revision = client.update(target, revision=revisionnumber)
            except pysvn.ClientError, e:
                # convert to a string
                log.warn("Updating %s failed: %s", target, str(e))
            else:
                if revision and revision[0] != -1:
                    log.info("%s at revision %r",
                             target,
                             revision[0].number)
                else:
                    log.warn("Something is wrong with your working "
                             "copy of %s", target)
        # svn without pysvn
        if self.config.configData['is_windows']:
            # win paths must be quoted (as literal strings)
            target = '\"%s\"'%target
            log.debug("windows updateSource: target is now [%s]",target)
        if not USE_PYSVN and not self.usecvs:
            command =  'svn up %s %s' % (versionoption, target)
            log.debug("Executing %s.", command)
            os.system(command)
        # cvs
        if self.usecvs:
            command =  'cvs up %s %s' % (versionoption, target)
            log.debug("Executing %s.", command)
            os.system(command)


    def attemptDownload(self):
        if not self.url:
            log.info("Set url for symlink for source %s."
                     % self.sourceName)
            return
        target = self._source()
        log.info("Checking out %s ...", target)

        if self.usecvs:
            # { 'url':'pserver:anonymous@cvs.zope.org:/cvs-repository CMFWiki CMF',
            # 'use_cvs': True,}
            # -> cvsroot   = pserver:anonymous@cvs.zope.org:/cvs-repository,
            #    cvspath   = CMF
            #    cvsmodule = CMFWiki
            cvsinfo = self.url.split(" ")
            cvsroot, cvsmodule = cvsinfo
            log.debug("Using cvs protocol")
            versionoption = self.version and "-r %s" % self.version or ""
            # temporary relative directory for cvs checkout
            relativetmp = tempfile.mkdtemp().split("/")[2]
            command = 'cvs -z3 -d %s co %s -d %s %s' % (
                cvsroot,
                versionoption,
                relativetmp,
                cvsmodule,
                )
            log.debug('commandline: %s', command)
            # Warning if is_windows:
            # commandline filepaths must be quoted as literals
            os.system(command)
            # I don't know if this is needed for os.rename ... IFH
            # if self.config.configData['is_windows']:
            #     # win paths must be quoted (as literal strings)
            #     target = '\"%s\"'%target
            #     log.debug("windows cvs attemptDownload: target is now [%s]",target)
            os.rename(relativetmp, target)
            message = "Checked out %s from %s " % (cvsmodule, cvsroot)
            message += (versionoption
                        and "version %s." % self.version
                        or ".")
            log.info(message)
        else:
            log.debug("Using svn protocol.")
            versionoption = self.version and "-r %s" % self.version or ""
            if self.config.configData['is_windows']:
                # win paths must be quoted (as literal strings)
                target = '\"%s\"'%target
                log.debug("windows svn attemptDownload: target is now [%s]",target)
            command = 'svn checkout %s %s %s' % (versionoption, self.url, target)
            os.system(command)
            log.info("Checked out from %s.", self.url)

class ConfigSource(SymlinkSource):
    """Wrapper around a symlink bundle source.
    """

    name = 'config'

    def _addProduct(self):
        # config sources only need to be downloaded, not linked.
        # Reload the total config, as the sources may have been updated.
        self.config.reloadConfig(self.config.configData['project'])

    def _updateSource(self):
        super(ConfigSource, self)._updateSource()
        # Reload the total config, as the sources may have been updated.
        self.config.reloadConfig(self.config.configData['project'])


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
            if self.pylib:
                target = os.path.join(self.libDir, includedFile)
            else:
                target = os.path.join(self.productDir, includedFile)
            if self.prepareInstall(target):
                utils.symlink(newSource, target, self.config)
                log.debug("Symlink added '%s'=>'%s'.", target, newSource)
                self._buildManifest(newSource, target)


class ArchiveSource(BaseSource):
    """Wrapper around an archive source.
    """

    name = 'archive'

    def __init__(self, sourceConfig, config, instanceDir):
        BaseSource.__init__(self, sourceConfig, config, instanceDir)
        if type(sourceConfig) == type(dict()):
            self.subPath = sourceConfig.get('sub_path', None)
        else:
            self.subPath = None

    def attemptDownload(self):
        if not self.url:
            return
        target = self._source()
        downloadDir = os.path.dirname(target)
        utils.makeDir(downloadDir) # creates it if not found.
        if self.url.endswith('/'):
            self.url = self.url + self.sourceName
        log.info("Downloading %s ...", target)
        urllib.urlretrieve(self.url, target)
        log.info("Downloaded from %s.", self.url)

    def moveDirs(self, tempDir):
        try:
            if self.pylib:
                baseDir = self.libDir
            else:
                baseDir = self.productDir
            if self.subPath:
                tempDir = os.path.join(tempDir, self.subPath)
                os.chdir(os.path.join(tempDir, '..'))
                log.debug("Appended sub-path '%s' to the extration "
                          "location.", self.subPath)
                extractedDirectory = self.subPath.split('/')[-1]
            else:
                extractedDirectory = os.listdir(tempDir)[0]
            target = os.path.join(baseDir, extractedDirectory)
            if extractedDirectory in self.drop:
                log.warn("Directory %s in droplist for %s, not installing it." %
                         (extractedDirectory, self.sourceName))
                return
            if self.prepareInstall(target):
                log.debug("Moving from %s to %s",
                          extractedDirectory, target)
                shutil.move(extractedDirectory, target)
                if self.userdefinedProductName:
                    os.rename(target,
                              os.path.join(self.productDir,
                                           self.userdefinedProductName))
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

    def _updateSource(self):
        """ Nothing to do, but we could redownload the zip and unzip it.
        """
        return

class ArchivebundleSource(ArchiveSource):
    """Wrapper around an archive bundle bundle.
    """

    name = 'archivebundle'

    def moveDirs(self, tempDir):
        extractedDirectories = os.listdir(tempDir)
        log.debug("Extracted dirs: %r.", extractedDirectories)

        if hasattr(self, 'instanceBundle') and self.instanceBundle:
            targetRoot = self.instanceDir
        else:
            targetRoot = self.productDir

        if len(extractedDirectories) ==  1:
            log.debug("One nice neat directory extracted, "
                      "moving its contents.")
            bundleDir = os.path.join(tempDir,
                                     extractedDirectories[0])
            os.chdir(bundleDir)
            extractedDirectories = os.listdir(bundleDir)
            log.debug("New extracted dirs: %r.", extractedDirectories)
        for extractedDirectory in extractedDirectories:
            target = os.path.join(targetRoot, extractedDirectory)
            if extractedDirectory in self.drop:
                log.warn("Directory %s in droplist for %s, not installing it." %
                         (extractedDirectory, self.sourceName))
                continue
            if not self.prepareInstall(target):
                continue
            if extractedDirectory in self.internalBundles:
                base_target = targetRoot
                # Plone 3.0 tar files contain Products and lib/python
                # as internalBundles.  Handle that correctly.
                if extractedDirectory == 'lib':
                    base_target = self.libDir
                    localDirs = os.listdir(extractedDirectory)
                    if localDirs == ['python']:
                        extractedDirectory = os.path.join(
                            extractedDirectory, 'python')
                        log.info('internal lib/python dir found')
                    else:
                        log.warn('Expected python in lib, but found %s',
                                 localDirs)
                log.info("Moving the contents of %s to %s.",
                          extractedDirectory, base_target)
                localDirs = os.listdir(extractedDirectory)
                for localDir in localDirs:
                    if '%s/%s' % (extractedDirectory, localDir) in self.drop:
                        log.warn("Directory %s in droplist for %s, not installing it." %
                         (localDir, self.sourceName))
                        continue
                    target = os.path.join(base_target, localDir)
                    if self.prepareInstall(target):
                        source = os.path.join(extractedDirectory,
                                              localDir)
                        shutil.move(source, target)
                        log.debug("Moved %s.", localDir)
                        self._buildManifest(localDir, target)
                continue
            shutil.move(extractedDirectory, target)
            log.debug("Moved %s.", extractedDirectory)
            self._buildManifest(extractedDirectory, target)

    def _updateSource(self):
        """ Nothing to do, but we could redownload the zip and unzip it.
        """
        return
