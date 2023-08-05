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
import transaction


class FakeRequest:
    """Support class needed for running reinstall for some products
    (like cmflinkchecker, that requires a REQUEST for the catalog
    updates it does).

    Lifted from Rafael Ritz's
    http://lists.plone.org/pipermail/setup/2005-November/000172.html
    """
 
    def __init__(self):
        self.form = {}
        
    def get(self, key, default=None):
        return self.form.get(key, default)

    def __getitem__(self, key):
        return self.get(key)

    def _hold(self, data):
        pass
    
    def __len__(self):
        return 0


class Reinstaller:

    def __init__(self, app):
        """Read the command line parameters and initialise.
        """

        self.app = app
        _policy=PermissiveSecurityPolicy()
        _oldpolicy=setSecurityPolicy(_policy)
        newSecurityManager(None,
                           OmnipotentUser().__of__(self.app.acl_users))
        self.app=makerequest(self.app)
        arguments = sys.argv[1:]
        print arguments
        if len(arguments) < 1:
            sys.exit("Not enough arguments.")
        self.ploneSiteName = arguments[0]
        self.mainProducts = arguments[1:]
        self.warnings = 0
        self.errors = 0

    def run(self):
        """Perform the actual process.
        """

        self.ensurePloneSiteExists()
        self.handleMigration()
        self.determineReinstallableProducts()
        self.reinstall()
        self.printErrors()
        transaction.commit()

    def ensurePloneSiteExists(self):
        """Ensure that the Plone Site actually exists.  Create it if
        does not.
        """

        if not hasattr(app, self.ploneSiteName):
            print 'INFO: Plone Site %s does not yet exist. Creating...' \
                  % self.ploneSiteName
            if hasattr(app.manage_addProduct['CMFPlone'], 'addPloneSite'):
                # plone 2.5
                factory = app.manage_addProduct['CMFPlone'].addPloneSite
            else:
                # plone 2.1
                factory = app.manage_addProduct['CMFPlone'].manage_addSite
            factory(self.ploneSiteName, self.ploneSiteName)
            transaction.commit()
        self.ploneSite = getattr(app, self.ploneSiteName, None)
        print 'INFO: %s' % self.ploneSite
        self.qi = self.ploneSite['portal_quickinstaller']

    def handleMigration(self):
        """See if plone itself needs migrating and do it if needed.
        """
        
        print "Determining if plone needs migrating..."
        pm = self.ploneSite['portal_migration']
        if pm.needUpgrading():
            request = FakeRequest()
            self.app.REQUEST = request
            print "Plone itself needs upgrading!"
            pm.upgrade(swallow_errors=1)
            del self.app.REQUEST
            transaction.commit()
            print "Migrated plone to latest version."
        else:
            print "Plone doesn't need to be migrated."

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
        request = FakeRequest()
        self.app.REQUEST = request
        for productId in self.reinstallableProducts:
            try:
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
        del self.app.REQUEST

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
