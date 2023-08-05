"""Configuration for instance manager
"""

# Directory in the user's homedir where we store our config.
CONFIGDIR = '.instancemanager'
SITECONFIG = '/etc/instancemanager/sitedefaults.py'
SECRET_PREFIX='local-'
STUB_PREFIX='stub.'

# Change these in zope.conf if development_machine == True.
DEBUGCONFIGCHANGES = {
    '#    security-policy-implementation python':
    'security-policy-implementation python\n',
    'verbose-security on': 'verbose-security on\n',
    'debug-mode on': 'debug-mode on\n',
    'devmode on': 'devmode on\n',
    }

CONFSNIPPETS = {
    # starttag name: list of search/replace strings.
    # Note that 'address ' has a space behind it to prevent it from
    # matching the "address" comment.
    'http-server': {'address ': 'address %(port)s'},
    #'server': {'address ': '  address %(port)s'},
    # http-server is for zope2 and zope3
    # 'server' is for using the Twisted server on Zope 3
    'ftp-server': {'address ': '  address %(ftp_port)s'},
    'webdav-source-server': {'address ': '  address %(webdav_port)s'},
    'icp-server': {'address ': '  address %(icp_port)s'},
    }

SNIPPETCONDITIONS = {
    # starttag name: variable that must be set in the config.
    'http-server': 'port',
    'server': 'port',
    'ftp-server': 'ftp_port',
    'webdav-source-server': 'webdav_port',
    'icp-server': 'icp_port',
    }

Z3FTPPORTSNIPPET= """<server ftp>
  type FTP
  address %(ftp_port)s
</server>
"""

LOGFILE = 'instancemanager.log'

QISCRIPT = 'quickreinstaller.py'
UISCRIPT = 'uninstaller.py'

PACKSCRIPT = 'pack.py'
 
CHANGEOWNSCRIPT = 'changeownership.py'

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
    %(zeo_client_line)s
  </zeoclient>
</zodb_db>
"""

Z3ZEOSNIPPET = """<zodb>
  <zeoclient>
    server localhost:%(zeoport)s
    storage 1
    # ZEO client cache, in bytes
    cache-size 20MB
    # Uncomment to have a persistent disk cache
    #client zeo1
  </zeoclient>
</zodb>
"""

DATABASE_TEMPFILES = [
    'Data.fs.tmp',
    'Data.fs.index',
    'Data.fs.lock',
    ]

APACHE_TEMPLATE = """
For the apache config:

  # Use the simple example at 
  # http://plone.org/documentation/tutorial/plone-apache/virtualhost
  # as your starting point.

  # Configuration for use with a squid that is configured using CacheFu.
  # Normalize URLs by removing trailing /'s
  RewriteRule ^/(.*)/$ http://127.0.0.1:3128/http/%(sn)s/80/$1 [L,P]
  # Pass all other urls straight through
  RewriteRule ^/(.*)$  http://127.0.0.1:3128/http/%(sn)s/80/$1 [L,P]

  # If you have zope directly behind apache, use the following;
  #RewriteRule ^(.*) http://localhost:%(zopeport)s/VirtualHostBase/http/%(sn)s:80/%(plonesite)s/VirtualHostRoot$1 [L,P]


For at the end of the cachefu squid.cfg (in CacheFuDocumentation/squid):

  yoursitenamehere.com: 127.0.0.1:%(zopeport)s/%(plonesite)s

"""
