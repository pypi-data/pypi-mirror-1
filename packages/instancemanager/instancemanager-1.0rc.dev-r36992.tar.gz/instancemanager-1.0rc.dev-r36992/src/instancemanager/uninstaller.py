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

class FakeRequest:
    """Support class needed for running reinstall for some products
    (like cmflinkchecker, that requires a REQUEST for the catalog
    updates it does).

    Lifted from Rafael Ritz's
    http://lists.plone.org/pipermail/setup/2005-November/000172.html
    """
 
    def __init__(self):
        self.form = {}
        self.cookies = {}
        self.maybe_webdav_client = False
        
    def get(self, key, default=None):
        return self.form.get(key, default)

    def set(self, key, value):
        self.form[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def _hold(self, data):
        pass
    
    def __len__(self):
        return 0

    def getPresentationSkin(self):
        return None

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

class Uninstaller:

    def __init__(self, app):
        """Read the command line parameters and initialise.
        """

        arguments = sys.argv[1:]
        print arguments
        if len(arguments) < 2:
            sys.exit("Not enough arguments.")
        self.ploneSiteName = arguments[0]
        self.adminUser = arguments[1]
        self.product = arguments[2]
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

        self.uninstall()
        self.printErrors()
        transaction_commit()


    def uninstall(self):
        """Do the actual reinstalling.
        """

        self.ploneSite = getattr(app, self.ploneSiteName, None)
        print 'INFO: %s' % self.ploneSite
        self.qi = self.ploneSite['portal_quickinstaller']
        print "Uninstalling..."
        try:
            request = FakeRequest()
            self.app.REQUEST = request
            response = FakeResponse()
            self.app.RESPONSE = response
            if self.qi.isProductInstalled(self.product):
                self.qi.uninstallProducts([self.product])
                print "Uninstall of %s succeeded." % self.product
            else:
                # Apparently main productId, but not installed. So we
                # install it instead of reinstalling it.
                print "%s is not installed so I have nothing to uninstall." % \
                    self.product
        except:
            print "ERROR: uninstall failed for %s!" % self.product
            self.errors += 1
        # Just do your best to kill these two:
        try:
            del self.app.REQUEST
        except:
            pass
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

uninstaller = Uninstaller(app)
uninstaller.run()
