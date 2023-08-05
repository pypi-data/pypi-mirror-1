"""Configuration for instance manager
"""

# Directory in the user's homedir where we store our config.
CONFIGDIR = '.instancemanager'

CONFIGCHANGES = {
    'address 8080': 'address %(port)s\n',
    'security-policy-implementation python':
    'security-policy-implementation python\n',
    'verbose-security on': 'verbose-security on\n',
    'debug-mode on': 'debug-mode on\n'
    }

ZEOCONFIGCHANGES = {}

LOGFILE = 'instancemanager.log'

QISCRIPT = 'quickreinstaller.py'

ZEOSNIPPET = """<zodb_db main>
  mount-point /
  # ZODB cache, in number of objects
  cache-size 500
  <zeoclient>
    server localhost:%(zeoport)s
    storage 1
    name zeostorage
    var $INSTANCE/var
    # ZEO client cache, in bytes
    cache-size 20MB
    # Uncomment to have a persistent disk cache
    #client zeo1
  </zeoclient>
</zodb_db>
"""

DATABASE_TEMPFILES = [
    'Data.fs.tmp',
    'Data.fs.index',
    'Data.fs.lock',
    ]
