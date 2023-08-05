"""Script that packs the database.

You can pass it an argument for the number of days of transactions to
keep in the database.
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


class Packer:

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
        if len(arguments) < 1:
            sys.exit("Not enough arguments.")
        self.days = arguments[0]
        self.days = int(self.days)

    def run(self):
        """Perform the actual process.
        """

        main = app.Control_Panel.Database['main']
        main.manage_pack(days=self.days)
        

packer = Packer(app)
packer.run()
