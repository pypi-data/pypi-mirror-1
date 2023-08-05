"""Script that calls the quickinstaller to reinstall all products. 

This script calls a plone site's quickinstaller and asks it to
re-install all products that can be updated. Products that aren't
installed will be left alone. 

Apart from that, you can pass it a list of "main products" that will
be reinstalled no matter what. If one of those main products isn't
installed yet, it will get a regular install.

Should the plone site need to be migrated, a migration is attempted.

The basis has been a script originally made by Maurits van Rees.  
"""

import sys
import os

try:
    from AccessControl.SecurityManagement import newSecurityManager
except:
    # Might be because we're called just to print our documentation
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(0)
    else:
        raise
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Testing.makerequest import makerequest
from Acquisition import Implicit
try:
    import transaction
except:
    # zope 2.7 BBB
    import ZODB
    transaction = False

def transaction_commit():
    if transaction:
        transaction.commit()
    else:
        # zope 2.7 BBB
        get_transaction().commit()
    

class OmnipotentUser( Implicit ):
    """
      Omnipotent User for installing several things.

      Adapted from Products.CMFCore.tests.base.security.  Using that
      exact code would give problems, because the site would be owned
      by 'all_powerful_Oz', not the usual admin user.  Going e.g. to
      the sharing tab of the front page would give TypeError:
      unsubscriptable object, because that 'all_powerful_Oz' is
      nowhere in acl_users.

    """
    def __init__(self, id):
        self.id = id
        
    def getId( self ):
        return self.id

    getUserName = getId

    def getRoles(self):
        return ('Manager',)

    def allowed( self, object, object_roles=None ):
        return 1

    def getRolesInContext(self, object):
        return ('Manager',)

    def _check_context(self, object):
        return True

    def has_permission(self, *args, **kwargs):
        return True

    def has_role(self, *args, **kwargs):
        return True


class FakeResponse:
    """Like the FakeRequest class above.  Needed for at least one of
    the products here at Zest Software.

    Thanks to Nuxeo:
    http://lists.nuxeo.com/pipermail/nuxeo-checkins/2006-May/012819.html
    which lists CPS3/products/CPSDashboards/trunk/testing.py
    """

    status = 0
    def __init__(self):
        self.cookies = {}

    def setCookie(self, cookie_id, cookie, path=None):
        self.cookies[cookie_id] = {
            'value': cookie, 'path': path}

    def expireCookie(self, arg, **kw):
        print "FakeResponse: called expireCookie with arg=%s" % arg

    # And from http://mail.zope.org/pipermail/cmf-checkins/2002-February/001830.html
    def setHeader(self, *args): pass
    def setStatus(self, status): self.status = status


class Reinstaller:

    def __init__(self, app):
        """Read the command line parameters and initialise.
        """

        arguments = sys.argv[1:]
        print arguments
        if len(arguments) < 2:
            sys.exit("Not enough arguments.")
        self.ploneSiteName = arguments[0]
        self.adminUser = arguments[1]
        args = arguments[2:]
        # Profiles for GenericSetup:
        self.profiles = [p for p in args if p.startswith('profile-')]
        self.mainProducts = [p for p in args if not p.startswith('profile-')]
        self.warnings = 0
        self.errors = 0
        self.app = app
        _policy=PermissiveSecurityPolicy()
        _oldpolicy=setSecurityPolicy(_policy)
        newSecurityManager(None,
                           OmnipotentUser(self.adminUser).__of__(self.app.acl_users))
        self.app=makerequest(self.app)

    def run(self):
        """Perform the actual process.
        """

        self.ensurePloneSiteExists()
        self.handleMigration()
        self.genericSetup()
        self.determineReinstallableProducts()
        self.reinstall()
        self.printErrors()
        transaction_commit()

    def ensurePloneSiteExists(self):
        """Ensure that the Plone Site actually exists.  Create it if
        does not.
        """

        if not hasattr(self.app, self.ploneSiteName):
            print 'INFO: Plone Site %s does not yet exist. Creating...' \
                  % self.ploneSiteName
            if hasattr(self.app.manage_addProduct['CMFPlone'], 'addPloneSite'):
                # plone 2.5
                factory = self.app.manage_addProduct['CMFPlone'].addPloneSite
            else:
                # plone 2.1
                factory = self.app.manage_addProduct['CMFPlone'].manage_addSite
            factory(self.ploneSiteName, self.ploneSiteName)
            transaction_commit()
        self.ploneSite = getattr(self.app, self.ploneSiteName, None)
        print 'INFO: %s' % self.ploneSite
        self.qi = self.ploneSite['portal_quickinstaller']

    def genericSetup(self):
        """Run steps from GenericSetup.
        """
        if len(self.profiles) == 0:
            print "No GenericSetup profiles specified."
            return
        try:
            from Products.CMFPlone.interfaces import IPloneSiteRoot
            from Products.GenericSetup import EXTENSION, profile_registry
            HAS_GENERICSETUP = True
        except ImportError:
            HAS_GENERICSETUP = False

        if HAS_GENERICSETUP == False:
            print "WARNING: GenericSetup wanted, but not available."
            self.warnings += 1
            return

        portal_setup = self.ploneSite.portal_setup
        for profile in self.profiles:
            print "Running GenericSetup for %s..." % profile
            try:
                portal_setup.setImportContext(profile)
                portal_setup.runAllImportSteps()
            except:
                print "ERROR: Running GenericSetup for %s failed." % profile
                self.errors += 1
            transaction_commit()

    def handleMigration(self):
        """See if plone itself needs migrating and do it if needed.
        """

        # In case of a upgrade from plone 2.0.5 to plone-2.1 with ATCT allready
        # installed, first reinstall ATCT before running migration.
        print "Determining if ATContentTypes needs to be reinstalled..."
        atct = 'ATContentTypes'
        self.qi = self.ploneSite['portal_quickinstaller']
        atct_installed = self.qi.isProductInstalled(atct)
        atct_tool = getattr(self.ploneSite, 'portal_atct', None)
        fs_version = self.qi.getProductVersion(atct)
        if (atct_installed and not atct_tool 
            and fs_version > '0.2.0-final (CVS/Unreleased)'):
            print "ATContentTypes needs reinstall before upgrading Plone"
	    self.qi.reinstallProducts([atct])
            transaction_commit()
            print "Reinstalled of ATContentTypes succeeded."
        else:
	    print "Reinstall of ATContentTypes is not needed."

        print "Determining if plone needs migrating..."
        pm = self.ploneSite['portal_migration']
        ploneVersion = pm.getInstanceVersion() # 2.5.2
        if '-' not in ploneVersion:
            ploneVersion = ploneVersion + '-zzz'
        availableVersions = []
        for version in pm.knownVersions():
            if '-' not in version:
                version = version + '-zzz'
            availableVersions.append(version)
        availableVersions.sort()
        latestVersion = availableVersions[-1]
        if ploneVersion != latestVersion:
            # migration needed.
            # pm.needUpgrading() also wants to update svn versions.
            print "Plone itself needs upgrading! (%s to %s)" %\
                (ploneVersion, latestVersion)
            pm.upgrade(swallow_errors=1)
            # And now to prevent (svn/dev) versions:
            latestVersion = latestVersion.replace('-zzz', '')
            pm.setInstanceVersion(latestVersion)
            transaction_commit()
            print "Migrated plone to latest version."
        else:
            print "Plone doesn't need to be migrated."

        print "Determining if ATContentTypes needs migrating..."
        atct_tool = getattr(self.ploneSite, 'portal_atct', None)
        if atct_tool:
            atctVersion = atct_tool.getVersion()[1] # [1] gives us the string.
            if ' ' in atctVersion:
                # Some "2.3.4 (svn/dev)" version, we'll just clean that
                # here to get an easier update.
                parts = atctVersion.split(' ')
                version = parts[0]
                version = version.replace('-devel', '-final')
                atct_tool.setInstanceVersion(version)
                atctVersion = version
            atctVersion = atctVersion.replace('-final', '-zzz')
            availableVersions = []
            for version in atct_tool.knownVersions():
                if '-' not in version:
                    version = version + '-zzz'
                version = version.replace('-final', '-zzz')
                availableVersions.append(version)
            availableVersions.sort()
            latestVersion = availableVersions[-1]
            if atctVersion < latestVersion:
                # ^^^ '<' instead of '!=' as somehow the atct version
                # can end up higher than the latest version...
                print "ATContentTypes needs upgrading! (%s to %s)"%\
                    (atctVersion, latestVersion)
                atct_tool.upgrade(swallow_errors=1)
                transaction_commit()
                # Now to keep the (svn/dev) versions out of there:
                latestVersion = latestVersion.replace('-zzz',
                                                      '-final')
                atct_tool.setInstanceVersion(latestVersion)
                print "Migrated ATContentTypes to latest version."
            else:
                print "ATContentTypes doesn't need to be migrated."

    def determineReinstallableProducts(self):
        """Determine which products need to be reinstalled.

        Everything that *is* reinstallable is selected. Non-installed
        products are left alone, except when they're in
        self.mainProducts, then they *have* to be explicitly
        installed.
        """

        self.reinstallableProducts = []
        print "Determining re-installable products..."
        for product in self.qi.listInstalledProducts():
            productId = product['id']
            if product['hasError'] == 1:
                print 'ERROR: %s has an error.' % productId
                self.errors += 1
            if product['isHidden'] == 1:
                print 'WARNING: %s is hidden.' % productId
                self.warnings += 1
            if product['isLocked'] == 1:
                print 'INFO: %s is locked.' % productId

            if (product['hasError'] == 0 and 
                product['isLocked'] == 0 and 
                product['isHidden'] == 0 and 
                product['installedVersion'] !=
                self.qi.getProductVersion(productId)):
                self.reinstallableProducts.append(productId)
                print "Re-installable: %s." % productId
        # Always reinstall the main products:
        for productId in self.mainProducts:
            if productId not in self.reinstallableProducts:
                self.reinstallableProducts.append(productId)
                print "Adding main product %s, too." % productId

    def reinstall(self):
        """Do the actual reinstalling.
        """

        print "Reinstalling..."
        for productId in self.reinstallableProducts:
            try:
                response = FakeResponse()
                self.app.RESPONSE = response
                if self.qi.isProductInstalled(productId):
                    self.qi.reinstallProducts([productId])
                    print "Reinstall of %s succeeded." % productId
                else:
                    # Apparently main productId, but not installed. So we
                    # install it instead of reinstalling it.
                    self.qi.installProduct(productId)
                    print "Installed %s (so no REinstall)." % \
                        productId
            except:
                print "ERROR: reinstall failed for %s!" % productId
                self.errors += 1
            try:
                del self.app.RESPONSE
            except:
                pass
    

    def printErrors(self):
        """Print feedback about errors/warnings.
        """

        if self.warnings > 0:
            print 'WARNING: %s warnings.' % self.warnings
        else:
            print 'INFO: no warnings.'

        if self.errors > 0:
            print 'WARNING: %s errors.' % self.errors
        else:
            print 'INFO: no errors.'

reinstaller = Reinstaller(app)
reinstaller.run()
